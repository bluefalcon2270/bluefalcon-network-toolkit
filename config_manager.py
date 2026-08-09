import os
import re

DEFAULT_TEMPLATE = """IPs:
1.1.1.1
8.8.8.8
9.9.9.9
208.67.222.222
1.0.0.1
8.8.4.4
94.140.14.14
8.26.56.26
76.76.2.0
64.6.64.6

Domains:
google.com
github.com
api.telegram.org
archive.ubuntu.com
cloudflare.com
speedtest.net
netflix.com
aws.amazon.com
wikipedia.org
bing.com

DNS:
1.1.1.1
8.8.8.8
9.9.9.9
208.67.222.222
94.140.14.14
209.244.0.3
1.1.1.2
8.26.56.26
185.228.168.9
76.76.19.19"""

class ConfigManager:
    @staticmethod
    def get_default():
        return DEFAULT_TEMPLATE

    @staticmethod
    def format_targets(content):
        ip_list = []
        domain_list = []
        dns_list = []
        
        current_section = "ip_list"
        
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"): continue
            
            lower_line = line.lower()
            if lower_line in ["ips:", "ip:"]:
                current_section = "ip_list"
                continue
            elif lower_line in ["domains:", "domain list:", "domain:"]:
                current_section = "domain_list"
                continue
            elif lower_line in ["dns list:", "dns:"]:
                current_section = "dns_list"
                continue
                
            parts = line.split(maxsplit=1)
            target = parts[0].strip()
            alias = parts[1].strip() if len(parts) > 1 else ""
            
            # Smart Detection: IPv4
            if re.match(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", target):
                formatted_item = f"{target} {alias}".strip()
                if current_section == "dns_list":
                    if formatted_item not in dns_list: dns_list.append(formatted_item)
                else:
                    if formatted_item not in ip_list: ip_list.append(formatted_item)
                continue
                
            # Smart Detection: Domain
            if re.match(r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$", target):
                formatted_item = f"{target} {alias}".strip()
                if formatted_item not in domain_list: domain_list.append(formatted_item)
                continue
                
            # Otherwise, stick to section
            formatted_item = f"{target} {alias}".strip()
            if current_section == "domain_list":
                if formatted_item not in domain_list: domain_list.append(formatted_item)
            elif current_section == "dns_list":
                if formatted_item not in dns_list: dns_list.append(formatted_item)
            else:
                if formatted_item not in ip_list: ip_list.append(formatted_item)
                if formatted_item not in ip_list: ip_list.append(formatted_item)
                
        ip_list = ConfigManager._deduplicate_list(ip_list)
        domain_list = ConfigManager._deduplicate_list(domain_list)
        dns_list = ConfigManager._deduplicate_list(dns_list)
                
        output = "IPs:\n"
        output += "\n".join(ip_list) if ip_list else ""
        output += "\n\nDomains:\n"
        output += "\n".join(domain_list) if domain_list else ""
        output += "\n\nDNS:\n"
        output += "\n".join(dns_list) if dns_list else ""
            
        data = {"ip_list": ip_list, "domain_list": domain_list, "dns_list": dns_list}
        return output.strip(), data

    @staticmethod
    def _deduplicate_list(items):
        seen = {}
        for item in items:
            parts = item.split(maxsplit=1)
            target = parts[0]
            name = parts[1] if len(parts) > 1 else ""
            
            if target not in seen:
                seen[target] = item
            else:
                existing_parts = seen[target].split(maxsplit=1)
                existing_name = existing_parts[1] if len(existing_parts) > 1 else ""
                
                if name and not existing_name:
                    seen[target] = f"{target} {name}"
                elif name and existing_name and name not in existing_name:
                    seen[target] = f"{target} {existing_name} / {name}"
                    
        return list(seen.values())

    @staticmethod
    def load_profile():
        if not os.path.exists("Profile.txt"):
            with open("Profile.txt", "w", encoding="utf-8") as f:
                f.write(DEFAULT_TEMPLATE)
            
        with open("Profile.txt", "r", encoding="utf-8") as f:
            content = f.read()
            
        _, data = ConfigManager.format_targets(content)
        return data
        
    @staticmethod
    def load_profile_raw():
        if not os.path.exists("Profile.txt"):
            with open("Profile.txt", "w", encoding="utf-8") as f:
                f.write(DEFAULT_TEMPLATE)
        with open("Profile.txt", "r", encoding="utf-8") as f:
            return f.read().strip()

    @staticmethod
    def save_profile(content):
        formatted, _ = ConfigManager.format_targets(content)
        with open("Profile.txt", "w", encoding="utf-8") as f:
            f.write(formatted.strip() + "\n")
        return formatted
