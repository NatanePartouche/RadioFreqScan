# 📡 RadioFreqScan

**RadioFreqScan** is an SDR (Software Defined Radio) tool for intelligently scanning and detecting active radio frequencies. It identifies transmissions based on power thresholds and visualizes them in real time through a modern Qt-based GUI.

---

## 🔍 Features

- 📶 Scan any defined frequency range
- 📈 Detect signal presence using power analysis
- 🖥️ Visual GUI for real-time visualization (via GNU Radio & PyQt5)
- 🔄 Dynamic frequency switching
- 💾 Optional logging of detected stations
- 🧩 Easily extensible with custom signal processing blocks

---

## 🛠️ Requirements

- Python 3.8+
- GNU Radio >= 3.10
- PyQt5
- SoapySDR (supports RTL-SDR, HackRF, etc.)
- An SDR-compatible USB device

### ✅ Install on Debian/Ubuntu

```bash
sudo apt install gnuradio python3-pyqt5 soapysdr-module-all
```

---

## 📁 Project Files

| File | Description |
|------|-------------|
| `power_detector.py` | GUI-based signal power detector |
| `power_detector.grc` | GNU Radio Companion file (graphical flow) |
| `scan_stations.py` | Scans a frequency band and logs active signals |
| `untitled.py` | Utility script (e.g. frequency switching or support logic) |
| `.pyc` files | Compiled Python helper files |
| `fmReceiver_.grc` | Sample FM receiver flowgraph (optional) |

---

## 🚀 Usage

1. Plug in your SDR device (e.g., RTL-SDR dongle)
2. Launch the main detection GUI:

```bash
python3 power_detector.py
```

3. Optionally, run background scanning:

```bash
python3 scan_stations.py
```

4. Results will appear in the GUI or logs depending on your configuration.

---

## 🧭 Example Use Cases

- Spectrum monitoring
- Emergency signal detection
- Radio environment awareness
- Automatic tuning of FM or other RF bands

---

## 🔮 Planned Improvements

- Signal classification (FM, AM, digital, noise)
- Web-based dashboard
- Geo-tagging with GPS
- Multi-threaded real-time logging

---


## 📜 License

This project is licensed under the [GNU GPLv3 License](https://www.gnu.org/licenses/gpl-3.0.html).

© 2025 RadioFreqScan Project
