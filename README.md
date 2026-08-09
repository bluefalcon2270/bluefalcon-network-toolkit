<div align="center">

# 🦅 BlueFalcon NTK (Network Toolkit)

**The ultimate all-in-one desktop application for asynchronous network diagnostics, DNS benchmarking, port scanning, and latency testing.**

![Windows](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@BlueFalcon2270)

<br />
</div>

An advanced, asynchronous desktop application designed to evaluate network configurations. Combining the power of our previous DNS Benchmark and Network Toolkit into one ultimate suite. It allows you to resolve domains, test TCP port accessibility, visualize ICMP ping latencies, and benchmark DNS servers through a sleek, unified Material Design 3 dark-mode dashboard.

## 🚀 Features

* **Unified Dashboard:** Four powerful tools in one app: Latency Scanner, Port Scanner, Domain Resolver, and DNS Benchmark.
* **Material Design 3 UI:** A completely redesigned, responsive dark-mode dashboard utilizing deep surfaces and custom color palettes.
* **Integrated Profile Manager:** Create, save, and load multiple configuration profiles (IPs, Domains, DNS) directly within the application.
* **Asynchronous Engines:** Run dozens of port, ping, and DNS tests simultaneously without the UI freezing using optimized asynchronous Python workers.
* **Instant Export:** Double-click domain results to instantly copy all unique IPs to your clipboard, or use the dedicated copy button.

<br>

## 💻 For Developers

The codebase utilizes a modular architecture separated into four main components for easier development:
1. `core.py`: Asynchronous network engines (ICMP, TCP, DNS resolving).
2. `ui_main.py`: Main application UI and logic handling.
3. `ui_views.py`: Dedicated file for rendering dynamic views (Profiles, About).
4. `config_manager.py`: File parsing and regex profile management.

**Requirements:**
Ensure you have Python 3.8+ and install the required UI framework:
```cmd
pip install customtkinter
```

**Compilation:**
To build your own standalone `.exe` file with the custom icon, activate your virtual environment and run PyInstaller against `main.py`:
```cmd
pyinstaller --noconsole --onefile --icon="icon.ico" --add-data "icon.ico;." --name "BlueFalcon NTK v1.0" "main.py"
```

<br>

## ✅ Supported Systems

* **Windows 11:** Fully Supported
* **Windows 10:** Fully Supported
