# 🦅 BlueFalcon NTK

![BlueFalcon NTK Screenshot](screenshot.png)

**BlueFalcon NTK** (Network Toolkit) is a powerful, lightning-fast, and extremely easy-to-use application designed for testing and analyzing network performance. Whether you're a gamer trying to find the best DNS server, or a system admin checking if your ports are open, this app does it all from one sleek interface!

---

## ✨ Features (In Simple Words)
- **Super Fast:** It does hundreds of tests at the exact same time, so you get your results in seconds, not minutes.
- **Latency Tester:** Easily check your ping to any IP address or domain using either standard ICMP (Ping) or TCP.
- **Port Scanner:** Quickly scan a website or IP to see exactly which doors (ports) are open or closed.
- **Domain Resolver:** Type in a website, and it will find every hidden IP address that runs it. You can even force it to use specific DNS servers!
- **DNS Benchmark:** Find out which DNS server is actually the fastest for *you*. It tests multiple DNS servers against multiple websites to find the absolute best connection.
- **Easy Profiles:** Save all your favorite IPs, websites, and DNS servers into a single file so you never have to type them twice.
- **Modern Dark Mode:** A beautiful, responsive interface that's easy on the eyes.

---

## 🚀 How to Use It

### 1. Download
The easiest way to get started is to simply download the latest `.exe` file from our [Releases](#) page. No installation required—just double-click and run!

### 2. The Tools
- **⏱️ Latency Tab:** Type in an IP or website, pick your protocol (ICMP or TCP), set your packet count, and hit start. It will show you your min, max, average ping, and jitter.
- **🔌 Port Tab:** Type in a target and the ports you want to check (like `80, 443, 8000-8010`). It will quickly blast through them and tell you exactly what's open.
- **🌐 Domain Tab:** Type in a website name to resolve it into IP addresses. You can toggle "Custom DNS" to use two specific DNS servers for the lookup instead of your computer's default.
- **🦅 DNS Tab:** This tests how fast your DNS servers are! Just hit start, and it will race all your configured DNS servers against your configured domains to see which DNS responds the fastest. Click the "🔽 Sort" button to instantly put the winner at the top.

### 3. Importing Your Own Lists (Profiles Tab)
Tired of typing the same IPs? 
1. Go to the **📁 Profiles** tab.
2. Click **Reset to Default** to get a template, or start typing your own lists of IPs, Domains, and DNS servers into the big text box.
3. Click **Save & Format**. The app will organize them perfectly!
4. From now on, whenever you run a test, your custom lists will automatically be loaded.
*(You can also click "Open Profile File" to edit your targets in a regular text editor!)*

---

## 💻 For Developers

If you want to run the app from source or compile it yourself:

### Prerequisites
Make sure you have Python 3.x installed. Then install the requirements:
```cmd
pip install customtkinter dnspython
```

### Running from Source
```cmd
python main.py
```

### Building the Executable (.exe)
You can compile your own standalone executable complete with the custom icon by running:
```cmd
pip install pyinstaller
pyinstaller --noconsole --onefile --icon="icon.ico" --add-data "icon.ico;." --name "BlueFalcon NTK v1.2" "main.py"
```
The finished `.exe` will be generated inside the `dist` folder!
