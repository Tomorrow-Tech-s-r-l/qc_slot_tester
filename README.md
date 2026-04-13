# QC Slot Tester

Quality Control tool for testing station hardware — LED boards and solenoids — via an Arduino board controlled through a Python GUI over a serial (USB) connection.

---

## Hardware Requirements

- Arduino board (Uno, Nano, Mega, etc.)
- LEDs connected to PWM-capable pins: **3, 5, 6, 9, 10, 11**
- Lock/relay module connected to pin **2**
- USB cable to connect the Arduino to your computer

## Software Requirements

- Python 3.9 or later (see macOS note below)
- Arduino IDE (to flash the firmware)

---

## Project Structure

```text
TestBoard/
├── .github/
│   └── workflows/
│       └── build.yml          # CI: builds macOS/Windows apps, verifies Arduino sketch
├── .vscode/
│   └── launch.json            # VS Code run/debug configuration
├── firmware/
│   └── firmware.ino           # Arduino firmware
├── app.py                     # Python GUI application (cross-platform)
├── requirements.txt           # Python dependencies
├── .gitignore
└── README.md
```

---

## Setup

### 1. Flash the Arduino

Open `firmware/firmware.ino` in the Arduino IDE, select your board and port, and click **Upload**.

### 2. Set up the Python environment

**macOS only — install Tk support first:**

Homebrew's Python does not bundle Tk. Install it before creating the venv,
making sure the version matches your Python (`python3 --version`):

```bash
brew install python-tk@3.14   # replace 3.14 with your actual version
```

If you already created a venv without doing this, delete it and start fresh:

```bash
rm -rf .venv
```

**All platforms — create the venv and install dependencies:**

```bash
# Create the virtual environment
python3 -m venv .venv

# Activate it:
#   macOS / Linux:
source .venv/bin/activate
#   Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the GUI

```bash
# With the venv active:
python app.py

# Or in VS Code: open the project and press F5 (uses .vscode/launch.json)
```

---

## Usage

1. Connect the Arduino via USB.
2. Click **Refresh Ports** to detect available serial ports.
3. Select your Arduino's port from the dropdown:
   - **macOS:** `/dev/tty.usbmodem*` or `/dev/tty.usbserial-*`
   - **Windows:** `COM3`, `COM4`, etc.
   - **Linux:** `/dev/ttyACM0`, `/dev/ttyUSB0`, etc.
4. Click **Connect** and wait ~2 seconds for the Arduino to boot.
5. Use the control buttons:
   - **LED ON / LED OFF** — controls all LEDs (pins 3, 5, 6, 9, 10, 11)
   - **Lock ON / Lock OFF** — controls the lock relay (pin 2)
6. Click **Disconnect** when done.

---

## Platform Notes

### macOS

- If your port does not appear, install the USB-Serial driver for your Arduino clone (CH340/CH341 chips used on many Nano clones require a separate driver).
- You may need to grant Terminal or VS Code access to serial devices under **System Settings → Privacy & Security**.
- Runs natively on Apple Silicon — no Rosetta needed.

### Windows

- A pre-built executable is available as a CI artifact from the GitHub Actions **Build** workflow (no Python required).
- If the port is not detected, check **Device Manager** to confirm the Arduino is recognised and note its COM port number.

---

## Serial Protocol

| Command      | Arduino Response | Effect                        |
|--------------|------------------|-------------------------------|
| `LED_ON`     | `OK:LED_ON`      | All LEDs on (~54% brightness) |
| `LED_OFF`    | `OK:LED_OFF`     | All LEDs off                  |
| `Lock_ON`    | `OK:Lock_ON`     | Lock engaged (pin 2 HIGH)     |
| `Lock_OFF`   | `OK:Lock_OFF`    | Lock disengaged (pin 2 LOW)   |
| `GET_STATUS` | `SYSTEM_OK`      | Health check                  |

On startup the Arduino sends `READY` to confirm it has finished booting.
Baud rate: **9600**

---

## CI / Build

Every push to `main` triggers three GitHub Actions jobs:

| Job                      | Runner           | Output                    |
| ------------------------ | ---------------- | ------------------------- |
| Build macOS App          | `macos-latest`   | `TestBoard.app` (artifact)|
| Build Windows Executable | `windows-latest` | `TestBoard.exe` (artifact)|
| Verify Arduino Sketch    | `ubuntu-latest`  | Compilation check only    |

Artifacts are available for download from the **Actions** tab on GitHub.
