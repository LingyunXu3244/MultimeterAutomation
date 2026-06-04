# HP 34401A Multimeter Testing Suite – User Guide

This guide explains how to set up and use the Python-based testing suite for the
**HP 34401A** digital multimeter over GPIB, including driver installation,
hardware connection, and full UI usage.

---

## 1. Overview

The suite provides a Python GUI (`voltage_ui.py`) that connects to the HP 34401A
over a GPIB interface (NI USB-GPIB adapter) and provides:

- Live measurement display
- Live trend chart
- Multiple measurement modes (DC voltage, AC voltage, resistance, continuity,
  diode, frequency, period)
- Min/Max/Mean statistics
- Configurable sampling interval and instrument settings
- Alarm thresholds
- CSV and Excel data export (with embedded chart)
- Presets for common measurement scenarios

A simpler command-line script (`import_pyvisa.py`) is also included for quick
verification or headless logging.

---

## 2. Hardware Requirements

| Item | Notes |
|------|-------|
| HP 34401A multimeter | Configured for GPIB (HP-IB) interface |
| NI USB-GPIB adapter | E.g. GPIB-USB-HS |
| GPIB cable | IEEE-488 cable, meter to adapter |
| Windows PC | Tested on Windows with Python 3.14 |
| Probes / DUT | Test leads, diodes, resistors, etc. depending on mode |

---

## 3. Multimeter Front Panel Setup

Before connecting via GPIB, configure the meter:

1. Power on the HP 34401A.
2. Press **Shift** → **I/O Menu**.
3. Select **2: INTERFACE** → set to `HP-IB / 488`.
4. Select **1: HP-IB ADDR** → set to a known address (suite default is `6`).
5. Connect the GPIB cable between the meter and the NI USB-GPIB adapter.
6. Plug the NI adapter into the PC.

---

## 4. Installing NI Drivers

The suite uses NI-VISA + NI-488.2 to talk to the meter through the NI USB-GPIB
adapter.

### 4.1 NI-VISA

During the NI-VISA installer **Additional items** selection, choose:

**Required**
- NI-VISA Runtime
- NI-VISA Configuration Support
- NI-VISA Interactive Control

**Optional but useful**
- NI I/O Trace (helps debug communication issues)

**Do NOT install**
- NI-VISA .NET development support
- NI-VISA .NET runtime
- NI-VISA C examples
- NI-VISA driver development wizard

Reboot after installation.

### 4.2 NI-488.2 (required for GPIB)

This is the actual GPIB driver. During its installer **Additional items** step,
select:

**Required**
- NI Hardware Config Utility
- NI 488.2 MAX Support
- NI 488.2 Utilities
- NI 488.2 DLL Direct Entry Support

**Optional**
- NI 488.2 Documentation

**Do NOT install** (not needed for Python use)
- NI 488.2 .NET dev support for Visual Studio 2010/2012/2013
- NI 488.2 .NET Language runtime 17.0.1 for .NET Framework 4.0
- NI 488.2 .NET Language runtime 17.0.1 for .NET Framework 4.5
- NI 488.2 C/C++ support
- NI 488.2 Visual Basic Support

Reboot after installation.

### 4.3 Verify in NI MAX

1. Open **NI MAX** (Measurement & Automation Explorer).
2. Expand **Devices and Interfaces**.
3. You should see your `GPIB0` interface.
4. Right-click `GPIB0` → **Scan for Instruments**.
5. Confirm the HP 34401A appears (default suite address: `6`).

If the meter does not appear:
- Check meter is set to HP-IB and powered on.
- Check the GPIB address matches what the suite expects.
- Reseat the GPIB cable and USB adapter.

---

## 5. Python Environment Setup

The suite uses a Python virtual environment in `.venv` inside the workspace.

### 5.1 Required packages

The following packages are required:

- `pyvisa`
- `matplotlib`
- `openpyxl`

These are typically already installed in `.venv` for this project.

To verify or reinstall manually, from Git Bash:

```bash
cd /c/chris/MultimeterAutomation
/c/chris/MultimeterAutomation/.venv/Scripts/python.exe -m pip install pyvisa matplotlib openpyxl
```

> **Note (Git Bash path syntax)**
> In Git Bash, Windows paths must use forward slashes and start with `/c/...`,
> not `c:/...`. For example:
> - Correct: `/c/chris/MultimeterAutomation/.venv/Scripts/python.exe`
> - Wrong: `/c:/chris/MultimeterAutomation/.venv/Scripts/python.exe`

---

## 6. First Connection Test

To confirm the meter is reachable, run the simple test script:

```bash
cd /c/chris/MultimeterAutomation
/c/chris/MultimeterAutomation/.venv/Scripts/python.exe import_pyvisa.py
```

Expected output:

```
VISA resources: ('ASRL3::INSTR', 'GPIB0::6::INSTR')
HEWLETT-PACKARD,34401A,0,7-5-2
DC voltage: +2.29700000E-05 V
DC voltage: +2.26630000E-05 V
...
```

Press `Ctrl+C` to stop.

If you see this output, the GPIB stack is working correctly and you can use the
UI.

### Common errors

| Error | Meaning | Fix |
|-------|---------|-----|
| `Could not locate a VISA implementation` | NI-VISA not installed | Install NI-VISA |
| `No module named 'gpib'` | NI-488.2 not installed | Install NI-488.2 |
| `VI_ERROR_LIBRARY_NFOUND` | VISA driver loaded but GPIB stack missing | Install NI-488.2 |
| `VI_ERROR_TMO` (timeout) | Occasional GPIB hiccup | The suite retries automatically |
| `GPIB0::6::INSTR` not found | Wrong address or meter not in HP-IB mode | Check meter I/O settings |

---

## 7. Launching the UI

From the workspace folder:

```bash
cd /c/chris/MultimeterAutomation
/c/chris/MultimeterAutomation/.venv/Scripts/python.exe voltage_ui.py
```

A dark-themed window titled **"HP 34401A Measurement Console"** will open.

---

## 8. UI Layout

The UI is organized top to bottom:

1. **Title bar** – Suite name and connection status.
2. **Live reading display** – Large numeric value with unit.
3. **Statistics row** – Count / Min / Max / Mean of current run.
4. **Controls panel** – Mode, sampling, instrument options, alarms, presets.
5. **Action buttons** – Connect/Stop/Export/Clear.
6. **Live chart** – Voltage (or reading) vs time.

---

## 9. Measurement Modes

Available modes in the **Mode** dropdown:

| Mode | Unit | Description |
|------|------|-------------|
| DC Voltage | V | Standard DC voltage measurement |
| AC Voltage | V | True-RMS AC voltage measurement |
| Resistance | Ω | 2-wire resistance measurement |
| Continuity | Ω | Beeper-style continuity test, fixed range |
| Diode | Vf | Forward voltage drop test for diodes |
| Frequency | Hz | Frequency of an input signal |
| Period | s | Period of an input signal |

### Notes

- **Continuity** and **Diode** are fixed-function tests with no range/NPLC
  controls.
- **AC Voltage** supports range selection but not NPLC or autozero.
- **Frequency** and **Period** use an **Aperture** (gate time) instead of NPLC.
- **DC Voltage** and **Resistance** support full controls: range, NPLC, autozero.

---

## 10. Controls Reference

### Sample interval (s)
How often a new reading is taken. Typical values: 0.2–1.0 s.

### NPLC
Integration time in power-line cycles (0.02, 0.2, 1, 10, 100).
- Lower = faster, noisier readings.
- Higher = slower, more stable, better noise rejection.

### Autozero
Removes internal offset before each reading. Improves accuracy for DC voltage
and resistance. Slightly slows acquisition.

### Auto range / Range
- **Auto range** lets the meter pick the best range.
- Disable and enter a fixed range (e.g. `10`) for stable measurements when the
  signal level is known.

### Aperture (s)
Gate time for Frequency / Period only. Options:
- 0.01 (fast, 4.5 digits)
- 0.1 (default, 5.5 digits)
- 1.0 (slow, 6.5 digits)

### Low alarm / High alarm + Enable alarm
If enabled, the live value turns red when the reading is below the low limit or
above the high limit.

### Presets
Preconfigured combinations of settings:

| Preset | Purpose |
|--------|---------|
| Fast | Short interval, low NPLC, no autozero |
| Stable Precision | Long NPLC, autozero on, fixed range |
| Diode Quick | Switches to Diode mode with quick sampling |
| AC Monitor | Switches to AC Voltage mode |
| Frequency Gate | Switches to Frequency mode with 0.1 s gate |

Click **Apply Preset** after selecting one.

### Single Read
Performs one reading without starting continuous mode. Useful for quick spot
checks. Cannot run during continuous acquisition.

---

## 11. Action Buttons

| Button | Function |
|--------|----------|
| Connect & Start | Connects to the meter and begins continuous acquisition |
| Stop | Stops acquisition and disconnects |
| Export CSV | Saves all collected readings to a CSV file |
| Export Excel | Saves all collected readings to an Excel workbook (with chart) |
| Clear Data | Resets the chart, statistics, and reading history |

---

## 12. Automatic Mode Switching

When you change the **Mode** dropdown while acquisition is running:

1. The graph and run history are cleared.
2. Acquisition is stopped cleanly.
3. The meter is reconnected and reconfigured for the new mode.
4. Acquisition resumes automatically in the new mode.

You do **not** need to press Stop and Start manually when switching modes.

---

## 13. Data Export

### CSV
Columns: `Mode, Timestamp, Reading, Settings`

Example:
```
DC Voltage,2026-05-21 14:23:11.452,1.23456,interval=0.5,nplc=1,...
```

### Excel
- Sheet "Readings": same data as CSV with formatted header.
- Sheet "Chart": embedded line chart of the trend.

Both export buttons open a Save As dialog with a timestamped default filename.

---

## 14. Typical Workflow Examples

### A. Logging a DC voltage rail
1. Set Mode = `DC Voltage`.
2. Apply preset = `Stable Precision`.
3. Optionally set Range = `10`.
4. Click **Connect & Start**.
5. Let it log for the desired period.
6. Click **Stop**, then **Export Excel**.

### B. Quickly testing a diode
1. Set Mode = `Diode`.
2. Connect red lead to anode, black to cathode.
3. Click **Single Read**.
4. A good silicon diode reads roughly 0.55–0.8 V.
5. Reverse the leads → should read `OL`.

### C. Checking continuity of a trace
1. Set Mode = `Continuity`.
2. Click **Connect & Start**.
3. Probe the two points.
4. Low resistance = good connection.

### D. Measuring frequency of a signal
1. Set Mode = `Frequency`.
2. Set Aperture = `0.1`.
3. Connect signal to the voltage input terminals.
4. Click **Connect & Start**.

---

## 15. Troubleshooting

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| UI shows ERROR after Start | Meter address mismatch | Confirm address `6` in NI MAX, update `RESOURCE` in the script if needed |
| `OL` shown in display | Signal exceeds current range | Switch to auto range or use a higher fixed range |
| Frequent timeouts | Cable / GPIB noise | Reseat cable, check connector, lower sample rate |
| Excel export fails | `openpyxl` missing | `pip install openpyxl` in the venv |
| Wrong colour for normal reading | Alarm enabled with wrong thresholds | Disable alarm or fix low/high values |
| `127` exit code from terminal | Bad path in Git Bash | Use `/c/...` not `/c:/...` |

---

## 16. File Reference

| File | Purpose |
|------|---------|
| `voltage_ui.py` | Main GUI application |
| `import_pyvisa.py` | Headless live-reading test script |
| `.venv/` | Python virtual environment with required packages |
| `e9d43e.pdf` | HP 34401A user manual (reference) |

---

## 17. Quick Reference Commands

```bash
# Launch UI
cd /c/chris/MultimeterAutomation
/c/chris/MultimeterAutomation/.venv/Scripts/python.exe voltage_ui.py

# Headless test
/c/chris/MultimeterAutomation/.venv/Scripts/python.exe import_pyvisa.py

# Reinstall packages
/c/chris/MultimeterAutomation/.venv/Scripts/python.exe -m pip install pyvisa matplotlib openpyxl
```

---

End of guide.
