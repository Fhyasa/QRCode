# QR Code Generator GUI

A simple Python GUI app to generate, save, and copy QR codes based on user input URLs or text.

Built with:
- `tkinter` (for GUI)
- `qrcode` (for QR code creation)
- `Pillow` (for image handling)
- `pywin32` (for clipboard copy on Windows)

---

## Features
- Enter any URL or text and instantly generate a QR code.
- Customize the size (box size) and border.
- Save the generated QR code as a PNG.
- Copy the QR code image directly to clipboard.
- Lightweight, fast, and easy-to-use interface.

---

## Run the App

```bash
QRCode.exe
```

---

## Build as an EXE
To compile into a standalone Windows executable (no console window):

```bash
pyinstaller --noconsole --onefile QRCode.py
```

> This will create a `.exe` file inside the `dist/` folder.

---
## Requirements
Install these Python packages:

```bash
pip install qrcode[pil] pillow pywin32
```

> **Note:** This script is for **Windows** because it uses `pywin32` for clipboard operations.

---

## License
This project is provided without any warranty. Free for personal and educational use.
