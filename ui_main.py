import os
import threading
import asyncio
import queue
import statistics
import customtkinter as ctk

from core import engine_ping_single, engine_port_single, engine_resolve_domain, engine_test_dns_domain
from config_manager import ConfigManager
from ui_shared import MD_BG, MD_SURFACE, MD_SURFACE_2, MD_SURFACE_3, MD_PRIMARY, MD_ON_PRIMARY, MD_TEXT, MD_TEXT_MUTED, MD_RED, MD_NAV_ACTIVE_BG, MD_NAV_ACTIVE_FG, ScrollableTable, APP_VERSION, TOOL_NAME, get_resource_path
from ui_views import ViewBuilder

class UltimateNetworkApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title(TOOL_NAME)
        self.geometry("1400x800")
        self.configure(fg_color=MD_BG)
        
        icon_path = get_resource_path("icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
            
        self.is_scanning = False
        self.abort_event = None
        self.ui_queue = queue.Queue(maxsize=10000)
        self.results_data = {}
        self.results_lock = threading.Lock()
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.views = {}
        self.build_sidebar()
        self.build_all_views()
        self.select_sidebar_frame("latency")

    # --- UI Queue processing ---
    def process_queue(self):
        try:
            processed = 0
            while not self.ui_queue.empty() and processed < 200:
                func, args = self.ui_queue.get_nowait()
                func(*args)
                processed += 1
        except queue.Empty: pass
        if self.is_scanning: self.after(30, self.process_queue)

    def dispatch_to_ui(self, func, *args):
        try: self.ui_queue.put_nowait((func, args))
        except queue.Full: pass 

    # --- Sidebar ---
    def build_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=MD_SURFACE)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        logo_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=(30, 30), sticky="w")
        ctk.CTkLabel(logo_frame, text="ULTIMATE", text_color=MD_PRIMARY, font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ctk.CTkLabel(logo_frame, text="Network Toolkit", text_color=MD_TEXT, font=("Segoe UI", 16)).pack(anchor="w")

        self.btn_nav_lat = ctk.CTkButton(self.sidebar_frame, text="⏱️ Latency", font=("Segoe UI", 15, "bold"), corner_radius=12, height=44, fg_color="transparent", text_color=MD_TEXT, anchor="w", command=lambda: self.select_sidebar_frame("latency"))
        self.btn_nav_lat.grid(row=1, column=0, sticky="ew", padx=15, pady=5)

        self.btn_nav_prt = ctk.CTkButton(self.sidebar_frame, text="🔌 Port", font=("Segoe UI", 15, "bold"), corner_radius=12, height=44, fg_color="transparent", text_color=MD_TEXT, anchor="w", command=lambda: self.select_sidebar_frame("port"))
        self.btn_nav_prt.grid(row=2, column=0, sticky="ew", padx=15, pady=5)

        self.btn_nav_dom = ctk.CTkButton(self.sidebar_frame, text="🌐 Domain", font=("Segoe UI", 15, "bold"), corner_radius=12, height=44, fg_color="transparent", text_color=MD_TEXT, anchor="w", command=lambda: self.select_sidebar_frame("domain"))
        self.btn_nav_dom.grid(row=3, column=0, sticky="ew", padx=15, pady=5)
        
        self.btn_nav_dns = ctk.CTkButton(self.sidebar_frame, text="🦅 DNS", font=("Segoe UI", 15, "bold"), corner_radius=12, height=44, fg_color="transparent", text_color=MD_TEXT, anchor="w", command=lambda: self.select_sidebar_frame("dns"))
        self.btn_nav_dns.grid(row=4, column=0, sticky="ew", padx=15, pady=5)

        self.btn_nav_profiles = ctk.CTkButton(self.sidebar_frame, text="📁 Profiles", font=("Segoe UI", 15, "bold"), corner_radius=12, height=44, fg_color="transparent", text_color=MD_TEXT, anchor="w", command=lambda: self.select_sidebar_frame("profiles"))
        self.btn_nav_profiles.grid(row=5, column=0, sticky="ew", padx=15, pady=5)

        self.btn_nav_about = ctk.CTkButton(self.sidebar_frame, text="ℹ️ About", font=("Segoe UI", 15, "bold"), corner_radius=12, height=44, fg_color="transparent", text_color=MD_TEXT, anchor="w", command=lambda: self.select_sidebar_frame("about"))
        self.btn_nav_about.grid(row=8, column=0, sticky="ew", padx=15, pady=20)

    def select_sidebar_frame(self, name):
        if self.is_scanning: return
        
        self.btn_nav_lat.configure(fg_color=MD_NAV_ACTIVE_BG if name == "latency" else "transparent", text_color=MD_NAV_ACTIVE_FG if name == "latency" else MD_TEXT)
        self.btn_nav_prt.configure(fg_color=MD_NAV_ACTIVE_BG if name == "port" else "transparent", text_color=MD_NAV_ACTIVE_FG if name == "port" else MD_TEXT)
        self.btn_nav_dom.configure(fg_color=MD_NAV_ACTIVE_BG if name == "domain" else "transparent", text_color=MD_NAV_ACTIVE_FG if name == "domain" else MD_TEXT)
        self.btn_nav_dns.configure(fg_color=MD_NAV_ACTIVE_BG if name == "dns" else "transparent", text_color=MD_NAV_ACTIVE_FG if name == "dns" else MD_TEXT)
        self.btn_nav_profiles.configure(fg_color=MD_NAV_ACTIVE_BG if name == "profiles" else "transparent", text_color=MD_NAV_ACTIVE_FG if name == "profiles" else MD_TEXT)
        self.btn_nav_about.configure(fg_color=MD_NAV_ACTIVE_BG if name == "about" else "transparent", text_color=MD_NAV_ACTIVE_FG if name == "about" else MD_TEXT)

        for view in self.views.values(): view.grid_forget()
        if name in self.views: self.views[name].grid(row=0, column=1, sticky="nsew")

    def refresh_sidebar_views(self):
        for name in ["profiles", "about"]:
            if name in self.views: self.views[name].destroy()
        self.views["profiles"] = ViewBuilder.build_profiles_view(self, self)
        self.views["about"] = ViewBuilder.build_about_view(self, self)

    def build_all_views(self):
        self.views["latency"] = ctk.CTkFrame(self, fg_color="transparent")
        self.build_latency_ui(self.views["latency"])
        
        self.views["port"] = ctk.CTkFrame(self, fg_color="transparent")
        self.build_port_ui(self.views["port"])
        
        self.views["domain"] = ctk.CTkFrame(self, fg_color="transparent")
        self.build_domain_ui(self.views["domain"])
        
        self.views["dns"] = ctk.CTkFrame(self, fg_color="transparent")
        self.build_dns_ui(self.views["dns"])

        self.views["profiles"] = ViewBuilder.build_profiles_view(self, self)
        self.views["about"] = ViewBuilder.build_about_view(self, self)
        
    def _create_top_card(self, parent, title):
        card = ctk.CTkFrame(parent, fg_color=MD_SURFACE, corner_radius=24)
        card.pack(fill="x", padx=30, pady=(30, 20), ipady=12)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=10)
        return inner

    def build_latency_ui(self, parent):
        inner = self._create_top_card(parent, "⏱️ Latency Scanner")
        
        ctk.CTkLabel(inner, text="Protocol:", font=("Segoe UI", 14, "bold"), text_color=MD_TEXT_MUTED).pack(side="left")
        self.in_lat_proto = ctk.CTkOptionMenu(inner, values=["ICMP", "TCP"], width=80, fg_color=MD_SURFACE_3, command=self.toggle_lat_port)
        self.in_lat_proto.set("ICMP")
        self.in_lat_proto.pack(side="left", padx=(5,15))
        
        ctk.CTkLabel(inner, text="Port:", font=("Segoe UI", 14, "bold"), text_color=MD_TEXT_MUTED).pack(side="left")
        self.in_lat_port = ctk.CTkEntry(inner, width=65, justify="center", fg_color=MD_SURFACE_3, border_width=0)
        self.in_lat_port.insert(0, "443")
        self.in_lat_port.pack(side="left", padx=(5,15))
        self.in_lat_port.configure(state="disabled", text_color=MD_TEXT_MUTED)
        
        ctk.CTkLabel(inner, text="Packets:", font=("Segoe UI", 14, "bold"), text_color=MD_TEXT_MUTED).pack(side="left")
        self.in_lat_pkts = ctk.CTkEntry(inner, width=65, justify="center", fg_color=MD_SURFACE_3, border_width=0)
        self.in_lat_pkts.insert(0, "10")
        self.in_lat_pkts.pack(side="left", padx=(5,15))
        
        ctk.CTkLabel(inner, text="Timeout(ms):", font=("Segoe UI", 14, "bold"), text_color=MD_TEXT_MUTED).pack(side="left")
        self.in_lat_time = ctk.CTkEntry(inner, width=65, justify="center", fg_color=MD_SURFACE_3, border_width=0)
        self.in_lat_time.insert(0, "1000")
        self.in_lat_time.pack(side="left", padx=(5,15))
        
        ctk.CTkLabel(inner, text="Workers:", font=("Segoe UI", 14, "bold"), text_color=MD_TEXT_MUTED).pack(side="left")
        self.in_lat_workers = ctk.CTkEntry(inner, width=65, justify="center", fg_color=MD_SURFACE_3, border_width=0)
        self.in_lat_workers.insert(0, "50")
        self.in_lat_workers.pack(side="left", padx=(5,15))

        self.btn_start_lat = ctk.CTkButton(inner, text="Start Test", font=("Segoe UI", 15, "bold"), fg_color=MD_PRIMARY, text_color=MD_ON_PRIMARY, command=lambda: self.toggle_scan("latency"))
        self.btn_start_lat.pack(side="right", padx=10)

        self.tbl_lat = ScrollableTable(parent)
        self.tbl_lat.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    def toggle_lat_port(self, choice):
        if choice == "TCP":
            self.in_lat_port.configure(state="normal", text_color=MD_TEXT)
        else:
            self.in_lat_port.configure(state="disabled", text_color=MD_TEXT_MUTED)

    def build_port_ui(self, parent):
        inner = self._create_top_card(parent, "🔌 Port Scanner")
        
        ctk.CTkLabel(inner, text="Ports:", font=("Segoe UI", 14, "bold"), text_color=MD_TEXT_MUTED).pack(side="left")
        self.in_port_num = ctk.CTkEntry(inner, width=150, justify="center", fg_color=MD_SURFACE_3, border_width=0)
        self.in_port_num.insert(0, "80, 443, 8000-8010")
        self.in_port_num.pack(side="left", padx=(5,15))
        
        ctk.CTkLabel(inner, text="Timeout(ms):", font=("Segoe UI", 14, "bold"), text_color=MD_TEXT_MUTED).pack(side="left")
        self.in_prt_time = ctk.CTkEntry(inner, width=65, justify="center", fg_color=MD_SURFACE_3, border_width=0)
        self.in_prt_time.insert(0, "2000")
        self.in_prt_time.pack(side="left", padx=(5,15))
        
        ctk.CTkLabel(inner, text="Workers:", font=("Segoe UI", 14, "bold"), text_color=MD_TEXT_MUTED).pack(side="left")
        self.in_prt_workers = ctk.CTkEntry(inner, width=65, justify="center", fg_color=MD_SURFACE_3, border_width=0)
        self.in_prt_workers.insert(0, "100")
        self.in_prt_workers.pack(side="left", padx=(5,15))

        self.btn_start_prt = ctk.CTkButton(inner, text="Start Test", font=("Segoe UI", 15, "bold"), fg_color=MD_PRIMARY, text_color=MD_ON_PRIMARY, command=lambda: self.toggle_scan("port"))
        self.btn_start_prt.pack(side="right", padx=10)

        self.tbl_prt = ScrollableTable(parent)
        self.tbl_prt.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    def build_domain_ui(self, parent):
        inner = self._create_top_card(parent, "🌐 Domain Resolver")
        
        self.dns_switch_var = ctk.StringVar(value="off")
        self.btn_dns_switch = ctk.CTkSwitch(inner, text="Custom DNS", variable=self.dns_switch_var, onvalue="on", offvalue="off", font=("Segoe UI", 14, "bold"), command=self.toggle_custom_dns)
        self.btn_dns_switch.pack(side="left", padx=(0,15))
        
        self.dns_inputs_frame = ctk.CTkFrame(inner, fg_color="transparent")
        
        ctk.CTkLabel(self.dns_inputs_frame, text="DNS 1:", font=("Segoe UI", 14, "bold"), text_color=MD_TEXT_MUTED).pack(side="left")
        self.in_dom_dns1 = ctk.CTkComboBox(self.dns_inputs_frame, values=[], width=130, fg_color=MD_SURFACE_3, command=self.update_dns_dropdowns)
        self.in_dom_dns1.set("")
        self.in_dom_dns1.pack(side="left", padx=(5,15))
        
        ctk.CTkLabel(self.dns_inputs_frame, text="DNS 2:", font=("Segoe UI", 14, "bold"), text_color=MD_TEXT_MUTED).pack(side="left")
        self.in_dom_dns2 = ctk.CTkComboBox(self.dns_inputs_frame, values=[], width=130, fg_color=MD_SURFACE_3, command=self.update_dns_dropdowns)
        self.in_dom_dns2.set("")
        self.in_dom_dns2.pack(side="left", padx=(5,15))
        
        self.dom_actions_frame = ctk.CTkFrame(inner, fg_color="transparent")
        
        ctk.CTkLabel(self.dom_actions_frame, text="Workers:", font=("Segoe UI", 14, "bold"), text_color=MD_TEXT_MUTED).pack(side="left")
        self.in_dom_threads = ctk.CTkEntry(self.dom_actions_frame, width=65, justify="center", fg_color=MD_SURFACE_3, border_width=0)
        self.in_dom_threads.insert(0, "50")
        self.in_dom_threads.pack(side="left", padx=(5,15))
        
        self.btn_export_dom = ctk.CTkButton(self.dom_actions_frame, text="Copy IPs", font=("Segoe UI", 13, "bold"), width=100, corner_radius=18, fg_color=MD_SURFACE_2, text_color=MD_TEXT, hover_color=MD_SURFACE_3, command=self.export_domain_ips)
        self.btn_export_dom.pack(side="left", padx=(0,10))
        
        self.dom_actions_frame.pack(side="left")
        
        self.btn_start_dom = ctk.CTkButton(inner, text="Start Test", font=("Segoe UI", 15, "bold"), fg_color=MD_PRIMARY, text_color=MD_ON_PRIMARY, command=lambda: self.toggle_scan("domain"))
        self.btn_start_dom.pack(side="right", padx=10)

        self.tbl_dom = ScrollableTable(parent)
        self.tbl_dom.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        self.tbl_dom.tree.bind("<Double-1>", self.on_domain_double_click)

    def update_dns_dropdowns(self, _=None):
        v1 = self.in_dom_dns1.get()
        v2 = self.in_dom_dns2.get()
        merged_data = ConfigManager.load_multiple_profiles(ConfigManager.get_available_profiles())
        all_dns = [d.split()[0] for d in merged_data.get("dns_list", [])]
        
        l1 = [d for d in all_dns if d != v2]
        l2 = [d for d in all_dns if d != v1]
        
        self.in_dom_dns1.configure(values=l1)
        self.in_dom_dns2.configure(values=l2)

    def toggle_custom_dns(self):
        if self.dns_switch_var.get() == "on":
            self.dns_inputs_frame.pack(side="left", before=self.dom_actions_frame)
            merged_data = ConfigManager.load_multiple_profiles(ConfigManager.get_available_profiles())
            dns_list = [d.split()[0] for d in merged_data.get("dns_list", [])]
            self.in_dom_dns1.configure(values=dns_list)
            self.in_dom_dns2.configure(values=dns_list)
            if dns_list:
                if len(dns_list) > 0: self.in_dom_dns1.set(dns_list[0])
                if len(dns_list) > 1: self.in_dom_dns2.set(dns_list[1])
        else:
            self.dns_inputs_frame.pack_forget()

    def on_domain_double_click(self, event):
        region = self.tbl_dom.tree.identify("region", event.x, event.y)
        if region in ("cell", "tree"):
            iid = self.tbl_dom.tree.focus()
            if iid:
                with self.results_lock:
                    data = self.results_data.get(iid, {})
                    ips = data.get("ips", [])
                if ips:
                    ip_text = "\n".join(ips)
                    self.clipboard_clear()
                    self.clipboard_append(ip_text)
                    import tkinter.messagebox
                    tkinter.messagebox.showinfo("Copied", "IPs copied to clipboard:\n\n" + ip_text)

    def export_domain_ips(self):
        ips_to_export = set()
        with self.results_lock:
            for d, data in self.results_data.items():
                if "ips" in data: ips_to_export.update(data["ips"])
        if not ips_to_export: return
        ip_text = "\n".join(ips_to_export)
        self.clipboard_clear()
        self.clipboard_append(ip_text)
        import tkinter.messagebox
        tkinter.messagebox.showinfo("Copied", "All unique IPs copied to clipboard:\n\n" + ip_text)

    def build_dns_ui(self, parent):
        inner = self._create_top_card(parent, "🦅 DNS Benchmark")
        
        ctk.CTkLabel(inner, text="Timeout(s):", font=("Segoe UI", 14, "bold"), text_color=MD_TEXT_MUTED).pack(side="left")
        self.in_dns_time = ctk.CTkEntry(inner, width=65, justify="center", fg_color=MD_SURFACE_3, border_width=0)
        self.in_dns_time.insert(0, "5.0")
        self.in_dns_time.pack(side="left", padx=(5,15))
        
        ctk.CTkLabel(inner, text="Workers:", font=("Segoe UI", 14, "bold"), text_color=MD_TEXT_MUTED).pack(side="left")
        self.in_dns_workers = ctk.CTkEntry(inner, width=65, justify="center", fg_color=MD_SURFACE_3, border_width=0)
        self.in_dns_workers.insert(0, "150")
        self.in_dns_workers.pack(side="left", padx=(5,15))
        
        self.btn_dns_sort = ctk.CTkButton(inner, text="🔽 Sort", font=("Segoe UI", 13, "bold"), width=80, corner_radius=18, fg_color="transparent", text_color=MD_TEXT, hover_color=MD_SURFACE_2, border_width=1, border_color=MD_SURFACE_3, command=self.sort_dns_results)
        self.btn_dns_sort.pack(side="left", padx=(5,15))
        
        self.btn_start_dns = ctk.CTkButton(inner, text="Start Test", font=("Segoe UI", 15, "bold"), fg_color=MD_PRIMARY, text_color=MD_ON_PRIMARY, command=lambda: self.toggle_scan("dns"))
        self.btn_start_dns.pack(side="right", padx=10)

        self.tbl_dns = ScrollableTable(parent)
        self.tbl_dns.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    def sort_dns_results(self):
        items = []
        for child in self.tbl_dns.tree.get_children():
            vals = self.tbl_dns.tree.item(child, "values")
            errs = float(vals[3]) if vals and len(vals) > 3 else 999
            ping = vals[4] if vals and len(vals) > 4 else "Failed"
            ping_val = float(ping.replace(" ms", "")) if "ms" in str(ping) else 99999
            items.append((child, errs, ping_val))
        items.sort(key=lambda x: (x[1], x[2]))
        for i, (child, errs, ping_val) in enumerate(items):
            self.tbl_dns.tree.move(child, "", i)
            vals = list(self.tbl_dns.tree.item(child, "values"))
            if vals:
                vals[0] = i + 1
                self.tbl_dns.tree.item(child, values=vals)


    # --- Scanner Implementations (Stubs to be filled next) ---
    def toggle_scan(self, mode):
        if self.is_scanning:
            if self.abort_event: self.abort_event.set()
            self.btn_start_lat.configure(text="Start Test", fg_color=MD_PRIMARY)
            self.btn_start_prt.configure(text="Start Test", fg_color=MD_PRIMARY)
            self.btn_start_dom.configure(text="Start Test", fg_color=MD_PRIMARY)
            self.btn_start_dns.configure(text="Start Test", fg_color=MD_PRIMARY)
            self.is_scanning = False
            return
            
        self.start_scan(mode)

    def start_scan(self, mode):
        while not self.ui_queue.empty(): self.ui_queue.get_nowait()
        
        tree = None
        if mode == "latency": tree = self.tbl_lat.tree
        elif mode == "port": tree = self.tbl_prt.tree
        elif mode == "domain": tree = self.tbl_dom.tree
        elif mode == "dns": tree = self.tbl_dns.tree
        
        for item in tree.get_children(): tree.delete(item)
            
        data_cfg = ConfigManager.load_single_profile(self.views["profiles"].winfo_children()[0].winfo_children()[0].winfo_children()[1].winfo_children()[0].cget("text") if hasattr(self, "dropdown_var") else "config_default.txt")
        merged_data = ConfigManager.load_multiple_profiles(ConfigManager.get_available_profiles())
        ips = merged_data.get("ip_list", [])
        domains = merged_data.get("domain_list", [])
        dns = merged_data.get("dns_list", [])

        with self.results_lock: self.results_data.clear()

        row_idx = 1
        scan_jobs = [] 
        
        if mode == "latency":
            try: count = int(self.in_lat_pkts.get())
            except: count = 10
            self._redraw_lat_headers(count)
            for h in ips + domains: scan_jobs.append((h.split()[0], h))
            if not scan_jobs: return
            with self.results_lock:
                for h, a in scan_jobs:
                    empty_pings = [""] * count
                    vals = [row_idx, h, f"0/{count}", "-", "-", "-", "-", "-"] + empty_pings
                    tree.insert("", "end", iid=h, values=vals, tags=("row_neutral",))
                    self.results_data[h] = {"count": count, "latencies": [], "idx": row_idx, "host": h}
                    row_idx += 1

        elif mode == "port":
            self._redraw_port_headers()
            try:
                clean_port_str = self.in_port_num.get().replace(" ", "")
                custom_ports = []
                for p_part in clean_port_str.split(','):
                    if not p_part: continue
                    if '-' in p_part:
                        start, end = map(int, p_part.split('-'))
                        if 1 <= start <= 65535 and 1 <= end <= 65535 and start <= end:
                            for port in range(start, end + 1):
                                custom_ports.append(port)
                    else:
                        port_int = int(p_part)
                        if 1 <= port_int <= 65535: custom_ports.append(port_int)
                custom_ports = sorted(list(set(custom_ports)))
            except:
                custom_ports = []
                    
            for h in ips + domains: scan_jobs.append((h.split()[0], h, custom_ports))
            if not scan_jobs or not custom_ports: return
            with self.results_lock:
                for h, a, pl in scan_jobs:
                    vals = [row_idx, h, f"0/{len(pl)}", "None"]
                    tree.insert("", "end", iid=h, values=vals, tags=("row_neutral",))
                    self.results_data[h] = {"total": len(pl), "tested": 0, "open_ports": [], "idx": row_idx, "host": h}
                    row_idx += 1

        elif mode == "domain":
            self._redraw_domain_headers(0)
            for h in domains: scan_jobs.append((h.split()[0], h))
            if not scan_jobs: return
            with self.results_lock:
                for h, a in scan_jobs:
                    tree.insert("", "end", iid=h, values=(row_idx, h, "PENDING", "-"), tags=("row_neutral",))
                    self.results_data[h] = {"idx": row_idx, "domain": h, "ips": []}
                    row_idx += 1
                    
        elif mode == "dns":
            self._redraw_dns_headers(domains)
            for d in dns:
                dns_ip = d.split()[0]
                scan_jobs.append(dns_ip)
            if not scan_jobs: return
            with self.results_lock:
                for dns_ip in scan_jobs:
                    a = [x for x in dns if x.startswith(dns_ip)][0]
                    # Format: id, address, name, status, ping, [domains...]
                    vals = [row_idx, dns_ip, a.replace(dns_ip, "").strip(), f"0/{len(domains)}", "PENDING"] + ["-"] * len(domains)
                    tree.insert("", "end", iid=dns_ip, values=vals, tags=("row_neutral",))
                    self.results_data[dns_ip] = {"idx": row_idx, "name": a.replace(dns_ip, "").strip(), "errors": 0, "tested": 0, "total": len(domains), "latencies": [], "dom_results": {dom: "-" for dom in domains}}
                    row_idx += 1

        self.btn_start_lat.configure(text="🛑 Stop", fg_color=MD_RED)
        self.btn_start_prt.configure(text="🛑 Stop", fg_color=MD_RED)
        self.btn_start_dom.configure(text="🛑 Stop", fg_color=MD_RED)
        self.btn_start_dns.configure(text="🛑 Stop", fg_color=MD_RED)
        
        self.is_scanning = True
        self.after(30, self.process_queue)
        
        def thread_worker():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.abort_event = asyncio.Event()
            if mode == "latency": loop.run_until_complete(self.async_run_latency(scan_jobs))
            elif mode == "port": loop.run_until_complete(self.async_run_port(scan_jobs))
            elif mode == "domain": loop.run_until_complete(self.async_run_domain(scan_jobs))
            elif mode == "dns": loop.run_until_complete(self.async_run_dns(scan_jobs))
            loop.close()
            self.dispatch_to_ui(self.task_completed)

        threading.Thread(target=thread_worker, daemon=True).start()

    def task_completed(self):
        self.is_scanning = False
        self.btn_start_lat.configure(text="Start Test", fg_color=MD_PRIMARY)
        self.btn_start_prt.configure(text="Start Test", fg_color=MD_PRIMARY)
        self.btn_start_dom.configure(text="Start Test", fg_color=MD_PRIMARY)
        self.btn_start_dns.configure(text="Start Test", fg_color=MD_PRIMARY)

    def _redraw_lat_headers(self, max_pings):
        self.tbl_lat.tree.configure(displaycolumns="#all")
        cols = ["idx", "host", "success", "avg", "med", "min", "max", "jitter"] + [f"ping_{i+1}" for i in range(max_pings)]
        self.tbl_lat.tree.configure(columns=cols)
        self.tbl_lat.tree.heading("idx", text="#", anchor="center"); self.tbl_lat.tree.column("idx", width=50, anchor="center", stretch=False)
        self.tbl_lat.tree.heading("host", text="Target", anchor="center"); self.tbl_lat.tree.column("host", width=250, anchor="w", stretch=False)
        self.tbl_lat.tree.heading("success", text="Status", anchor="center"); self.tbl_lat.tree.column("success", width=100, anchor="center", stretch=False)
        self.tbl_lat.tree.heading("avg", text="Avg", anchor="center"); self.tbl_lat.tree.column("avg", width=90, anchor="center", stretch=False)
        self.tbl_lat.tree.heading("med", text="Median", anchor="center"); self.tbl_lat.tree.column("med", width=90, anchor="center", stretch=False)
        self.tbl_lat.tree.heading("min", text="Min", anchor="center"); self.tbl_lat.tree.column("min", width=90, anchor="center", stretch=False)
        self.tbl_lat.tree.heading("max", text="Max", anchor="center"); self.tbl_lat.tree.column("max", width=90, anchor="center", stretch=False)
        self.tbl_lat.tree.heading("jitter", text="Jitter", anchor="center"); self.tbl_lat.tree.column("jitter", width=90, anchor="center", stretch=False)
        for i in range(max_pings):
            self.tbl_lat.tree.heading(f"ping_{i+1}", text=f"P {i+1}", anchor="center")
            self.tbl_lat.tree.column(f"ping_{i+1}", width=80, anchor="center", stretch=False)

    def _redraw_port_headers(self):
        self.tbl_prt.tree.configure(displaycolumns="#all")
        cols = ["idx", "host", "status", "open"]
        self.tbl_prt.tree.configure(columns=cols)
        self.tbl_prt.tree.heading("idx", text="#", anchor="center"); self.tbl_prt.tree.column("idx", width=50, anchor="center", stretch=False)
        self.tbl_prt.tree.heading("host", text="Target", anchor="center"); self.tbl_prt.tree.column("host", width=250, anchor="w", stretch=False)
        self.tbl_prt.tree.heading("status", text="Status", anchor="center"); self.tbl_prt.tree.column("status", width=100, anchor="center", stretch=False)
        self.tbl_prt.tree.heading("open", text="Open Ports", anchor="center"); self.tbl_prt.tree.column("open", width=450, anchor="center", stretch=False)

    def _redraw_domain_headers(self, max_ips):
        self.tbl_dom.tree.configure(displaycolumns="#all")
        cols = ["idx", "domain", "status", "total"] + [f"ip_{i+1}" for i in range(max_ips)]
        self.tbl_dom.tree.configure(columns=cols)
        self.tbl_dom.tree.heading("idx", text="#", anchor="center"); self.tbl_dom.tree.column("idx", width=50, anchor="center", stretch=False)
        self.tbl_dom.tree.heading("domain", text="Domain", anchor="center"); self.tbl_dom.tree.column("domain", width=250, anchor="w", stretch=False)
        self.tbl_dom.tree.heading("status", text="Status", anchor="center"); self.tbl_dom.tree.column("status", width=100, anchor="center", stretch=False)
        self.tbl_dom.tree.heading("total", text="IPs", anchor="center"); self.tbl_dom.tree.column("total", width=100, anchor="center", stretch=False)
        for i in range(max_ips):
            self.tbl_dom.tree.heading(f"ip_{i+1}", text=f"IP {i+1}", anchor="center")
            self.tbl_dom.tree.column(f"ip_{i+1}", width=150, anchor="center", stretch=False)

    def _redraw_dns_headers(self, domains):
        self.tbl_dns.tree.configure(displaycolumns="#all")
        cols = ["idx", "address", "name", "status", "ping"] + domains
        self.tbl_dns.tree.configure(columns=cols)
        self.tbl_dns.tree.heading("idx", text="#", anchor="center"); self.tbl_dns.tree.column("idx", width=50, anchor="center", stretch=False)
        self.tbl_dns.tree.heading("address", text="DNS Address", anchor="center"); self.tbl_dns.tree.column("address", width=180, anchor="w", stretch=False)
        self.tbl_dns.tree.heading("name", text="DNS Name", anchor="center"); self.tbl_dns.tree.column("name", width=140, anchor="w", stretch=False)
        self.tbl_dns.tree.heading("status", text="Status", anchor="center"); self.tbl_dns.tree.column("status", width=100, anchor="center", stretch=False)
        self.tbl_dns.tree.heading("ping", text="Avg Ping (ms)", anchor="center"); self.tbl_dns.tree.column("ping", width=120, anchor="center", stretch=False)
        for d in domains:
            self.tbl_dns.tree.heading(d, text=d.split()[0], anchor="center")
            self.tbl_dns.tree.column(d, width=120, anchor="center", stretch=False)

    # --- Updates ---
    def update_lat_row(self, host, new_val):
        with self.results_lock:
            if host not in self.results_data: return
            d = self.results_data[host]
            d["latencies"].append(new_val)
            valid = [v for v in d["latencies"] if v is not None]
            succ = len(valid)
            tot = d["count"]
            stat_str = f"{succ}/{tot}"
            raw_pings = [f"{int(v)} ms" if v is not None else "FAIL" for v in d["latencies"]]
            while len(raw_pings) < tot: raw_pings.append("")

            if not valid:
                vals = [d["idx"], d["host"], stat_str, "FAIL", "FAIL", "FAIL", "FAIL", "-"] + raw_pings
                self.tbl_lat.tree.item(host, values=vals, tags=("row_error",))
                return

            avg = round(sum(valid) / len(valid)); med = round(statistics.median(valid))
            mn = round(min(valid)); mx = round(max(valid))
            jitter = round(sum(abs(valid[i] - valid[i-1]) for i in range(1, len(valid))) / max(1, len(valid)-1)) if len(valid)>1 else 0

            tag = "row_error" if succ == 0 else "row_warning" if succ < tot or avg > 150 else "row_success"
            vals = [d["idx"], d["host"], stat_str, f"{avg} ms", f"{med} ms", f"{mn} ms", f"{mx} ms", f"{jitter} ms"] + raw_pings
            self.tbl_lat.tree.item(host, values=vals, tags=(tag,))
            
    def update_port_row(self, host, port, val):
        with self.results_lock:
            if host not in self.results_data: return
            d = self.results_data[host]
            d["tested"] += 1
            if val is not None:
                d["open_ports"].append(int(port))
            
            d["open_ports"].sort()
            
            stat_str = f"{d['tested']}/{d['total']}"
            open_str = ", ".join(map(str, d["open_ports"])) if d["open_ports"] else "None"
            
            tag = "row_success" if len(d["open_ports"]) == d["total"] else "row_warning" if len(d["open_ports"]) > 0 else "row_neutral"
            vals = [d["idx"], d["host"], stat_str, open_str]
            self.tbl_prt.tree.item(host, values=vals, tags=(tag,))

    def update_domain_row(self, domain, ip_list, err):
        with self.results_lock:
            if domain not in self.results_data: return
            d = self.results_data[domain]
            if err:
                self.tbl_dom.tree.item(domain, values=(d["idx"], d["domain"], "FAILED", "-"), tags=("row_error",))
                return
            tag = "row_success" if ip_list else "row_warning"
            current_cols = list(self.tbl_dom.tree["columns"])
            req = len(ip_list); cur = len(current_cols) - 4 
            if cur < req: self._redraw_domain_headers(req)
            vals = [d["idx"], d["domain"], "SUCCESS", len(ip_list)] + ip_list
            self.tbl_dom.tree.item(domain, values=vals, tags=(tag,))

    def update_dns_row(self, dns_ip, domain, ok, time_str, raw):
        with self.results_lock:
            if dns_ip not in self.results_data: return
            d = self.results_data[dns_ip]
            
            d["tested"] += 1
            if not ok:
                d["errors"] += 1
            else:
                try: d["latencies"].append(float(time_str.replace(" ms", "")))
                except: pass
            
            d["dom_results"][domain] = time_str
            
            avg_ping = f"{round(sum(d['latencies'])/len(d['latencies']))} ms" if d["latencies"] else "FAIL"
            stat_str = f"{d['tested']}/{d['total']}"
            
            dom_vals = [d["dom_results"][dom] for dom in list(self.tbl_dns.tree["columns"])[5:]]
            
            vals = [d["idx"], dns_ip, d["name"], stat_str, avg_ping] + dom_vals
            tag = "row_error" if d["errors"] == len(d["dom_results"]) else "row_warning" if d["errors"] > 0 else "row_success"
            self.tbl_dns.tree.item(dns_ip, values=vals, tags=(tag,))

    # --- Async Runners ---
    async def async_run_latency(self, scan_jobs):
        try: timeout_ms = int(self.in_lat_time.get())
        except: timeout_ms = 1000
        protocol = self.in_lat_proto.get()
        try: workers = int(self.in_lat_workers.get())
        except: workers = 50
        
        target_port = None
        if protocol == "TCP":
            try: target_port = int(self.in_lat_port.get())
            except: target_port = 443
            
        sem = asyncio.Semaphore(workers)
        async def ping_target(host, count):
            for _ in range(count):
                if self.abort_event.is_set(): break
                async with sem:
                    val = await engine_ping_single(host, timeout_ms, self.abort_event, protocol, target_port)
                self.dispatch_to_ui(self.update_lat_row, host, val)
        tasks = []
        for h, a in scan_jobs:
            with self.results_lock: count = self.results_data[h]["count"]
            tasks.append(ping_target(h, count))
        await asyncio.gather(*tasks)

    async def async_run_port(self, scan_jobs):
        try: timeout_ms = int(self.in_prt_time.get())
        except: timeout_ms = 2000
        try: workers = int(self.in_prt_workers.get())
        except: workers = 100
        sem = asyncio.Semaphore(workers)
        async def port_target(host, port):
            async with sem:
                if self.abort_event.is_set(): return
                val = await engine_port_single(host, port, timeout_ms / 1000.0, self.abort_event)
                self.dispatch_to_ui(self.update_port_row, host, port, val)
        tasks = []
        for h, a, p_list in scan_jobs:
            for p in p_list: tasks.append(port_target(h, p))
        await asyncio.gather(*tasks)

    async def async_run_domain(self, scan_jobs):
        try: workers = int(self.in_dom_threads.get())
        except: workers = 50
        
        dns_servers = None
        if self.dns_switch_var.get() == "on":
            dns_servers = []
            d1 = self.in_dom_dns1.get().strip()
            d2 = self.in_dom_dns2.get().strip()
            if d1: dns_servers.append(d1)
            if d2: dns_servers.append(d2)
            
        sem = asyncio.Semaphore(workers)
        async def resolve_target(host):
            async with sem:
                if self.abort_event.is_set(): return
                domain, ip_list, err = await engine_resolve_domain(host, sem, self.abort_event, dns_servers)
                self.dispatch_to_ui(self.update_domain_row, domain, ip_list, err)
        tasks = [resolve_target(h) for h, a in scan_jobs]
        await asyncio.gather(*tasks)

    async def async_run_dns(self, scan_jobs):
        try: timeout_sec = float(self.in_dns_time.get())
        except: timeout_sec = 5.0
        try: workers = int(self.in_dns_workers.get())
        except: workers = 150
        sem = asyncio.Semaphore(workers)
        
        merged_data = ConfigManager.load_multiple_profiles(ConfigManager.get_available_profiles())
        domains = merged_data["domain_list"]
        
        async def resolve_dns(dns_ip, dom):
            async with sem:
                if self.abort_event.is_set(): return
                ok, time_str, raw = await engine_test_dns_domain(dns_ip, dom, timeout_sec, sem, self.abort_event)
                self.dispatch_to_ui(self.update_dns_row, dns_ip, dom, ok, time_str, raw)
                
        tasks = []
        for dns_ip in scan_jobs:
            for dom in domains:
                tasks.append(resolve_dns(dns_ip, dom))
        await asyncio.gather(*tasks)
