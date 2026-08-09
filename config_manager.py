import os
import re

class ConfigManager:
    @staticmethod
    def get_available_profiles():
        profiles = [f for f in os.listdir('.') if f.startswith('config_') and f.endswith('.txt')]
        if not profiles:
            default = "config_default.txt"
            ConfigManager.save_single_profile(default, {"dns_list": [], "domain_list": [], "ip_list": []})
            return [default]
        return sorted(profiles)

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
                
        formatted = "IPs:\n"
        for item in ip_list: formatted += f"{item}\n"
        formatted += "\nDomains:\n"
        for item in domain_list: formatted += f"{item}\n"
        formatted += "\nDNS:\n"
        for item in dns_list: formatted += f"{item}\n"
            
        data = {"ip_list": ip_list, "domain_list": domain_list, "dns_list": dns_list}
        return formatted.strip(), data

    @staticmethod
    def load_single_profile(filename):
        if not os.path.exists(filename):
            return {"ip_list": [], "domain_list": [], "dns_list": []}
            
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
            
        _, data = ConfigManager.format_targets(content)
        return data

    @staticmethod
    def load_multiple_profiles(filenames):
        merged_data = {"ip_list": [], "domain_list": [], "dns_list": []}
        seen_ips = set(); seen_domains = set(); seen_dns = set()
        
        for fname in filenames:
            data = ConfigManager.load_single_profile(fname)
            for item in data.get("ip_list", []):
                if item not in seen_ips: seen_ips.add(item); merged_data["ip_list"].append(item)
            for item in data.get("domain_list", []):
                if item not in seen_domains: seen_domains.add(item); merged_data["domain_list"].append(item)
            for item in data.get("dns_list", []):
                if item not in seen_dns: seen_dns.add(item); merged_data["dns_list"].append(item)
                
        return merged_data

    @staticmethod
    def save_single_profile(filename, data):
        formatted = "IPs:\n"
        for item in data.get("ip_list", []): formatted += f"{item}\n"
        formatted += "\nDomains:\n"
        for item in data.get("domain_list", []): formatted += f"{item}\n"
        formatted += "\nDNS:\n"
        for item in data.get("dns_list", []): formatted += f"{item}\n"
            
        with open(filename, "w", encoding="utf-8") as f:
            f.write(formatted.strip() + "\n")
