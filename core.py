import asyncio
import platform
import re
import socket
import os
import time
import subprocess
import dns.resolver

def _sync_resolve(domain: str, dns_servers: list = None):
    domain = domain.strip()
    
    if dns_servers:
        for dns_server in dns_servers:
            dns_server = dns_server.strip()
            if not dns_server: continue
            
            try:
                system = platform.system().lower()
                creationflags = subprocess.CREATE_NO_WINDOW if "windows" in system else 0
                cmd = ["nslookup", domain, dns_server]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5, creationflags=creationflags)
                
                output = result.stdout
                lines = output.split('\n')
                
                ip_list = []
                parsing_answers = False
                for line in lines:
                    line = line.strip()
                    if not line: continue
                    
                    if line.lower().startswith("name:"):
                        parsing_answers = True
                    elif parsing_answers and (line.lower().startswith("address:") or line.lower().startswith("addresses:")):
                        parts = line.split(":", 1)
                        if len(parts) == 2:
                            ip = parts[1].strip()
                            if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip):
                                ip_list.append(ip)
                    elif parsing_answers and re.match(r"^\d{1,3}(\.\d{1,3}){3}$", line):
                        ip_list.append(line)
                        
                if ip_list:
                    return (domain, ip_list, None)
            except Exception:
                pass 
        
        return (domain, [], "All custom DNS servers failed")
    
    try:
        ip_list = socket.gethostbyname_ex(domain)[2]
        return (domain, ip_list, None)
    except socket.gaierror:
        return (domain, [], "Resolution failed")
    except OSError as e:
        return (domain, [], f"OS Error: {e}")

async def engine_resolve_domain(domain: str, sem: asyncio.Semaphore, abort_event: asyncio.Event = None, dns_servers: list = None):
    async with sem:
        if abort_event and abort_event.is_set():
            return (domain, [], "Aborted")
        return await asyncio.to_thread(_sync_resolve, domain, dns_servers)

async def engine_ping_single(ip, timeout_ms=1000, abort_event: asyncio.Event = None, protocol="icmp", port=None):
    if abort_event and abort_event.is_set():
        return None
        
    if protocol.lower() == "tcp" and port is not None:
        return await engine_port_single(ip, port, timeout_ms / 1000.0, abort_event)
        
    system = platform.system().lower()
    count_flag = "-n" if "windows" in system else "-c"
    timeout_flag = "-w" if "windows" in system else "-W"
    timeout_val = str(timeout_ms) if "windows" in system else str(max(1, timeout_ms // 1000))

    kwargs = {}
    if "windows" in system:
        kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW

    cmd = ["ping", count_flag, "1", timeout_flag, timeout_val, ip]
    
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            **kwargs
        )
        
        if abort_event:
            abort_task = asyncio.create_task(abort_event.wait())
            comm_task = asyncio.create_task(proc.communicate())
            done, pending = await asyncio.wait([abort_task, comm_task], return_when=asyncio.FIRST_COMPLETED)
            
            if abort_task in done:
                proc.kill()
                return None
            else:
                stdout, _ = comm_task.result()
        else:
            stdout, _ = await proc.communicate()
            
        output = stdout.decode('utf-8', errors='ignore')

        if proc.returncode == 0:
            time_val = None
            if "windows" in system:
                match = re.search(r"time[=<](\d+)ms", output, re.IGNORECASE)
                if match: time_val = float(match.group(1))
            else:
                match = re.search(r"time=([\d\.]+)\s*ms", output, re.IGNORECASE)
                if match: time_val = float(match.group(1))
            return time_val if time_val is not None else 0.0
    except Exception:
        pass
    return None

async def engine_port_single(ip, port, timeout_sec=2.0, abort_event: asyncio.Event = None):
    if abort_event and abort_event.is_set():
        return None
        
    try:
        t0 = time.time()
        conn = asyncio.open_connection(ip, port)
        
        if abort_event:
            abort_task = asyncio.create_task(abort_event.wait())
            conn_task = asyncio.create_task(asyncio.wait_for(conn, timeout=timeout_sec))
            done, pending = await asyncio.wait([abort_task, conn_task], return_when=asyncio.FIRST_COMPLETED)
            
            if abort_task in done:
                for task in pending: task.cancel()
                return None
            else:
                reader, writer = conn_task.result()
        else:
            reader, writer = await asyncio.wait_for(conn, timeout=timeout_sec)
            
        dt = (time.time() - t0) * 1000
        writer.close()
        await writer.wait_closed()
        return dt
    except Exception:
        return None

def tcp_test(ip, port, timeout):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        t0 = time.time()
        sock.connect((ip, port))
        dt = (time.time() - t0) * 1000
        sock.close()
        return True, round(dt)
    except Exception:
        return False, "TCP Err"

def _sync_test_dns_domain(dns_ip, domain, timeout):
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = [dns_ip]
    resolver.timeout = timeout
    resolver.lifetime = timeout
    try:
        ans = resolver.resolve(domain, "A")
        ips = [x.to_text() for x in ans]
        if not ips: return False, "No IP", 0
        ok, t_res = tcp_test(ips[0], 443, timeout)
        if ok: return True, f"{t_res} ms", t_res
        else: return False, str(t_res), 0
    except Exception: return False, "?", 0

async def engine_test_dns_domain(dns_ip, domain, timeout_sec, sem: asyncio.Semaphore, abort_event: asyncio.Event = None):
    async with sem:
        if abort_event and abort_event.is_set():
            return False, "Aborted", 0
        return await asyncio.to_thread(_sync_test_dns_domain, dns_ip, domain, timeout_sec)
