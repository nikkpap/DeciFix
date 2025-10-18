# 🧮 DeciFIX – Windows Decimal Settings Helper

**DeciFIX** is a lightweight Windows GUI utility built in **Python (Tkinter)** to automatically fix your **decimal and thousand separators** for engineering, surveying, and Excel workflows.

Designed for professionals who need consistent numeric formats across **Excel**, **AutoCAD**, **Civil 3D**, and **Topographic tools**.

---

## 🚀 Features

- ✅ **Apply dot-decimal format** (`1000000.111`)
- ✅ **Disable thousand grouping**
- 🔄 **Restore default Greek/European settings**
- 🟢 **LED indicator** (green/red) for current system state
- ⚙️ **Registry-based modification** under `HKCU\Control Panel\International`
- 🧰 **Open Region dialog** (`intl.cpl`) directly
- 🔐 **Run as Administrator** (optional prompt)
- ♻️ **Reboot button** for full system refresh
- 🆘 **Help → Instructions / About** with registry mapping table
- 💾 **No CMD window** (pure GUI with `pythonw.exe`)

---

## 📷 Screenshot

*(Optional – add a screenshot of your GUI here)*  
Example:  
![DeciFIX Screenshot](docs/screenshot.png)

---

## 🧩 Registry Keys Affected

| GUI (Control Panel → Region → Additional Settings → Numbers) | Registry Key | Example Value |
| ------------------------------------------------------------- | ------------- | -------------- |
| Decimal symbol | `sDecimal` | `.` |
| Digit grouping symbol | `sThousand` | *(space)* or `.` |
| Digit grouping | `sGrouping` | `3;0` or `0` |
| List separator | `sList` | `;` |
| Measurement system | `iMeasure` | `0` = Metric |
| Number of digits after decimal | `iDigits` | `2` |
| Negative number format | `iNegNumber` | `1` |
| Currency → Decimal symbol | `sMonDecimalSep` | `.` |
| Currency → Digit grouping symbol | `sMonThousandSep` | *(space)* or `.` |
| Currency → Digit grouping | `sMonGrouping` | `3;0` or `0` |

---

## ⚡ Installation

### 1️⃣ Requirements
- Windows 10 / 11  
- Python **3.13+** or **3.14+** installed  
- Tkinter (included by default)  

### 2️⃣ Run

#### Option A – Double-click
Associate `.pyw` files with `pythonw.exe`:
