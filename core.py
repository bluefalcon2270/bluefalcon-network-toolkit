import asyncio
import platform
import re
import socket
import os
import time
import subprocess
import dns.resolver

def _sync_resolve(domain: str, dns_servers: list = None, timeout_ms: int = 5000):
    domain = domain.strip()
    
    if dns_servers:
        for dns_server in dns_servers:
            dns_server = dns_server.strip()
            if not dns_server: continue
            
            try:
                system = platform.system().lower()
                creationflags = subprocess.CREATE_NO_WINDOW if "windows" in system else 0
                cmd = ["nslookup", domain, dns_server]
                t_sec = max(1, timeout_ms // 1000)
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=t_sec, creationflags=creationflags)
                
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

async def engine_resolve_domain(domain: str, abort_event: asyncio.Event = None, dns_servers: list = None, timeout_ms: int = 5000):
    if abort_event and abort_event.is_set():
        return (domain, [], "Aborted")
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(_sync_resolve, domain, dns_servers, timeout_ms),
            timeout=timeout_ms / 1000.0
        )
    except (asyncio.TimeoutError, TimeoutError):
        return (domain, [], "Timeout")

async def engine_ping_single(ip, timeout_ms=1000, abort_event: asyncio.Event = None, protocol="icmp", port=None):
    if abort_event and abort_event.is_set():
        return None
        
    if protocol.lower().startswith("tcp") and port is not None:
        l7_mode = (protocol.lower() == "tcp-l7")
        return await engine_port_single(ip, port, timeout_ms / 1000.0, abort_event, l7_mode=l7_mode)
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

async def engine_port_single(ip, port, timeout_sec=2.0, abort_event: asyncio.Event = None, l7_mode=False):
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
        
        if l7_mode:
            read_timeout = min(0.5, timeout_sec / 2)
            l7_success = False
            try:
                data = await asyncio.wait_for(reader.read(1024), timeout=read_timeout)
                if data and b"SSH-" in data:
                    l7_success = True
            except asyncio.TimeoutError:
                try:
                    writer.write(b"GET / HTTP/1.1\r\nHost: " + ip.encode() + b"\r\n\r\n")
                    await writer.drain()
                    data = await asyncio.wait_for(reader.read(1024), timeout=timeout_sec - read_timeout)
                    if data:
                        l7_success = True
                except Exception:
                    pass
            except Exception:
                pass
                
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
                
            if not l7_success:
                return None
            return dt
            
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
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
        else: return False, "FAIL", 0
    except Exception: return False, "FAIL", 0

async def engine_test_dns_domain(dns_ip, domain, timeout_sec, abort_event: asyncio.Event = None):
    if abort_event and abort_event.is_set():
        return False, "Aborted", 0
    return await asyncio.to_thread(_sync_test_dns_domain, dns_ip, domain, timeout_sec)
