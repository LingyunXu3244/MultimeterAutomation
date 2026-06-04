# DMM Control GUI — Engineering Spec-let

**Document type:** Lab-Automation Building Block Spec-let
**Building block:** DMM Control GUI (HP 34401A over GPIB)
**Status:** Draft
**Owner / Point of contact:** Lingyun Xu (lingyun.xu@intel.com)
**Last updated:** 2026-06-04
**Validated against:** HP 34401A (firmware `7-5-2` per `*IDN?`), Python 3.10,
NI-VISA + NI-488.2, PyVISA 1.16, matplotlib 3.10, openpyxl 3.1

> **Structure note:** This document follows the team speclet structure defined in
> `SKILL.md` (Table of Contents → Intro/Background/Scope → Boundaries →
> Requirements → Setup → How to Use → Common Errors).

> **Image placeholders:** `📷 [IMAGE: ...]` marks where a photo or screenshot
> should be inserted. Items marked *(Will be added later)* are pending capture.

---

## Table of Contents
1. [Intro / Background / Scope](#1-intro--background--scope)
   - [1.1 Background](#11-background)
   - [1.2 Scope](#12-scope)
   - [1.3 Use Cases](#13-use-cases)
   - [1.4 Why It's Complicated](#14-why-its-complicated)
   - [1.5 How It's Currently Being Done (Full Capabilities)](#15-how-its-currently-being-done-full-capabilities)
   - [1.6 How It's Going To Be Done (Captured Capabilities)](#16-how-its-going-to-be-done-captured-capabilities)
2. [Boundaries](#2-boundaries)
   - [2.1 Device Limitations](#21-device-limitations)
   - [2.2 Implementation / Automation Limitations](#22-implementation--automation-limitations)
   - [2.3 Manual vs Automated Capability Matrix](#23-manual-vs-automated-capability-matrix)
   - [2.4 Specifications & Operating Limits](#24-specifications--operating-limits)
3. [Requirements / Pre-requisites](#3-requirements--pre-requisites)
   - [3.1 Hardware](#31-hardware)
   - [3.2 Protections](#32-protections-optional)
   - [3.3 Software Tools](#33-software-tools)
4. [Setup Steps](#4-setup-steps)
5. [How To Use It](#5-how-to-use-it)
6. [Common Errors](#6-common-errors)
7. [Appendix — Open Questions, Glossary, Legend](#7-appendix)

---

## 1. Intro / Background / Scope

### 1.1 Background
Bench digital multimeters (DMMs) like the **HP/Agilent 34401A** are workhorse lab
instruments, but by default they are operated by hand from the front panel and
read out one value at a time. For any measurement that needs to be **logged over
time, repeated reliably, or shared**, manual operation becomes the bottleneck.

The **DMM Control GUI** is a lab-automation building block: a desktop application
that connects to the 34401A over GPIB, configures it, streams live readings,
plots them, and exports the logged data to CSV/Excel.

### 1.2 Scope
**In scope**
- Automated configuration and live acquisition from a **single** HP 34401A.
- Multiple measurement modes (DC/AC voltage, resistance, continuity, diode,
  frequency, period).
- Live numeric display, trend chart, running statistics, alarms.
- Data export to CSV and Excel (with embedded chart).

**Out of scope (current version)**
- Multi-instrument / multi-channel orchestration (single meter only).
- Closed-loop control or automated pass/fail sequencing.
- Headless / scripted (no-GUI) operation.
- Integration into GTAX.
- Instruments other than the 34401A (though the SCPI design is portable — TBD).

### 1.3 Use Cases

| # | Use Case | Description |
|---|----------|-------------|
| 1 | Power-rail logging | Monitor a DC voltage rail over minutes/hours, capture min/max/mean and drift. |
| 2 | Diode / junction check | Single-read forward voltage of a diode; verify ~0.55–0.8 V (Si) and `OL` reverse. |
| 3 | Continuity testing | Verify a trace/connection shows low resistance. |
| 4 | Resistance measurement | 2-wire resistance logging with NPLC/autozero for stability. |
| 5 | AC voltage monitoring | True-RMS AC voltage trend over time. |
| 6 | Frequency / period capture | Measure signal frequency or period using a gate (aperture) time. |
| 7 | Data hand-off | Export a timestamped run to Excel for analysis or reporting. |

### 1.4 Why It's Complicated

- **Instrument communication stack:** Talking to the 34401A requires a layered
  driver stack (NI-488.2 GPIB driver → NI-VISA → PyVISA → SCPI). Any missing
  layer produces cryptic failures.
- **SCPI quirks:** Function changes must be sequenced carefully (`*CLS`, `CONF`,
  `*OPC?`) or the meter parses sub-commands against the wrong function and lights
  the **ERR** annunciator. Range syntax is `<func>:RANG:AUTO ON|OFF` — the
  "obvious" `RANG AUTO` is invalid.
- **Per-mode capability differences:** Not all modes support the same controls
  (NPLC, autozero, aperture, range). The UI must enable/disable controls per mode.
- **Concurrency:** Acquisition runs on a background thread while Tkinter owns the
  UI thread. Sessions must be opened/closed cleanly so a restarting thread does
  not destroy a newer thread's instrument session.
- **Transient GPIB errors:** Occasional VISA timeouts require retry logic rather
  than aborting the run.
- **Overload / edge values:** Readings can come back as `OL` (overload) and must
  be handled gracefully in display, stats, and plotting.

### 1.5 How It's Currently Being Done (Full Capabilities)

The 34401A itself (and the current GUI) supports the following. This is the
**superset** of what the hardware can do.

#### Measurement modes & controls

| Mode | Unit | Range control | NPLC | Autozero | Aperture |
|------|------|---------------|------|----------|----------|
| DC Voltage | V | Yes | Yes | Yes | — |
| AC Voltage | V | Yes | — | — | — |
| Resistance (2-wire) | Ω | Yes | Yes | Yes | — |
| Continuity | Ω | Fixed | — | — | — |
| Diode | V (Vf) | Fixed | — | — | — |
| Frequency | Hz | Yes | — | — | Yes |
| Period | s | Yes | — | — | Yes |

#### Hardware capabilities (from 34401A datasheet — confirm against `e9d43e.pdf`)

| Capability | Value | Status |
|------------|-------|--------|
| Resolution | up to 6½ digits | confirm |
| DC Voltage ranges | 100 mV / 1 V / 10 V / 100 V / 1000 V | TBD — verify |
| AC Voltage ranges | 100 mV – 750 V | TBD — verify |
| Resistance ranges | 100 Ω – 100 MΩ | TBD — verify |
| Frequency range | 3 Hz – 300 kHz | TBD — verify |
| Reading rate (max) | up to ~1000 rdgs/s (low resolution) | TBD — verify |
| Reading memory | ~512 readings (instrument buffer) | TBD — verify |
| Interfaces | GPIB (HP-IB) and RS-232 | confirm |

#### GUI capabilities (today)
- Live numeric display with unit and alarm color-coding.
- Live trend chart (rolling 300-point window).
- Running statistics: Count, Min, Max, Mean (per active mode).
- Configurable sample interval, NPLC, autozero, range/auto-range, aperture.
- Low/High alarm thresholds with enable toggle.
- Presets: Fast, Stable Precision, Diode Quick, AC Monitor, Frequency Gate.
- Single Read (one-shot) and continuous acquisition.
- Automatic mode-switch (reconfigures meter live when mode changes).
- CSV export and Excel export (with embedded line chart).

### 1.6 How It's Going To Be Done (Captured Capabilities)

This section describes **how much** of the full hardware capability the GUI
building block actually captures. (See the full side-by-side in
[§2.3 Manual vs Automated Capability Matrix](#23-manual-vs-automated-capability-matrix).)

| Hardware capability | Captured by GUI? | Notes |
|---------------------|------------------|-------|
| DC Voltage | ✅ Full | Range, NPLC, autozero exposed |
| AC Voltage | ✅ Partial | Range only (no NPLC/autozero — not applicable) |
| Resistance (2-wire) | ✅ Full | Range, NPLC, autozero exposed |
| Resistance (4-wire) | ❌ Not yet | Not in mode table — TBD |
| DC Current | ❌ Not yet | Not implemented — TBD |
| AC Current | ❌ Not yet | Not implemented — TBD |
| Continuity | ✅ Full | Fixed-function |
| Diode | ✅ Full | Fixed-function |
| Frequency | ✅ Full | Aperture exposed |
| Period | ✅ Full | Aperture exposed |
| Max hardware reading rate | ⚠️ Limited | Effective rate = software interval + conversion time; raw rate not yet characterized (TBD) |
| Instrument reading buffer | ⚠️ Not used | Readings stored in PC memory, not instrument buffer |

**Summary:** The GUI captures the most common voltage/resistance/diagnostic modes
at moderate sample rates suitable for logging and monitoring. High-speed burst
capture, current modes, and 4-wire resistance are **not yet** implemented.

---

## 2. Boundaries

### 2.1 Device Limitations
What the **hardware physically cannot do**, regardless of the software:

- **Single function at a time** — cannot measure, e.g., voltage and current
  simultaneously; one measurement function is active per acquisition.
- **Single input channel** — no built-in multi-channel scanning without an
  external switch/multiplexer unit.
- **Not a high-speed digitizer** — max ~1000 rdgs/s at low resolution; high
  resolution (6½ digits) is much slower.
- **Limited on-board memory** — instrument reading buffer holds ~512 readings.
- **Input ceilings** — capped at ~1000 V DC / 750 V AC (see [§3.2](#32-protections-optional)).
- **2-wire vs 4-wire trade-off** — 2-wire resistance includes lead resistance;
  true 4-wire requires the dedicated sense terminals.

### 2.2 Implementation / Automation Limitations
What the **automation does not (yet) support**, even though the device can:

- **No current modes** — DC/AC current are not implemented in the GUI.
- **No 4-wire resistance** — only 2-wire is exposed.
- **Instrument trigger/buffer unused** — the GUI polls `READ?` rather than using
  hardware triggering or on-board buffering.
- **Hardcoded address** — resource fixed at `GPIB0::6::INSTR` (`RESOURCE` constant).
- **Single instrument only** — no multi-meter orchestration.
- **GUI-only** — no headless/scripted/API mode; not integrated into GTAX.
- **Effective sample rate** — bounded by software interval + conversion time, not
  the raw hardware reading rate.

### 2.3 Manual vs Automated Capability Matrix

Legend: ✅ supported · ⚠️ partial · ❌ not available / locked off.

| Feature / Capability | Manual (front panel) | Automated (GUI) | Notes / Locked off |
|----------------------|:-------------------:|:---------------:|--------------------|
| DC Voltage | ✅ | ✅ | Range / NPLC / autozero exposed |
| AC Voltage | ✅ | ⚠️ | Range only (NPLC/autozero N/A) |
| Resistance (2-wire) | ✅ | ✅ | Full controls |
| Resistance (4-wire) | ✅ | ❌ | **Locked off** — not implemented |
| DC Current | ✅ | ❌ | **Locked off** — not implemented |
| AC Current | ✅ | ❌ | **Locked off** — not implemented |
| Continuity | ✅ | ✅ | Fixed-function |
| Diode | ✅ | ✅ | Fixed-function |
| Frequency | ✅ | ✅ | Aperture exposed |
| Period | ✅ | ✅ | Aperture exposed |
| Instrument MATH (Null/dB/dBm/Limit) | ✅ | ⚠️ | GUI does its own Min/Max/Mean + alarms; instrument MATH unused |
| External / single triggering | ✅ | ⚠️ | GUI uses `READ?` polling; no external trigger |
| On-board reading buffer (~512) | ✅ | ❌ | **Not used** — readings stored on PC |
| Data logging to file | ❌ (manual transcription) | ✅ | CSV / Excel — **automation advantage** |
| Live trend chart | ❌ | ✅ | **Automation advantage** |
| Running statistics | ❌ (manual) | ✅ | Count / Min / Max / Mean |
| Alarms / threshold flags | ⚠️ (limited) | ✅ | Color-coded low/high alarms |
| Presets / one-click config | ❌ | ✅ | 5 presets |
| Remote / automated config | ❌ | ✅ | SCPI over VISA |
| Multi-instrument | ❌ | ❌ | **Locked off** — single meter only |
| Headless / scripted run | ❌ | ❌ | **Not yet** — GUI only |

### 2.4 Specifications & Operating Limits

#### Specifications Summary

| Parameter | Value |
|-----------|-------|
| Device | HP/Agilent 34401A (6½-digit DMM) |
| Interface | GPIB (IEEE-488), NI USB-GPIB adapter |
| Protocol | SCPI over NI-VISA |
| VISA resource | `GPIB0::6::INSTR` (default address 6) |
| Default sample interval | 0.5 s |
| Chart window | 300 points (`MAX_POINTS`) |
| Read retries | 3 (`MAX_RETRIES`) |
| Fastest sample rate (observed) | TBD — needs measurement |
| Slowest sample rate (observed) | TBD — needs measurement |
| Max test duration tested | TBD — needs measurement |

#### Operating boundaries & limits

| Boundary | Limit | Limited by |
|----------|-------|------------|
| Sample interval | ≥ ~0.5 s default (configurable) | Software interval + NPLC/aperture conversion time |
| Max test duration | TBD | PC RAM (readings held in memory list) |
| Trend chart history | 300 most-recent points | `MAX_POINTS` (full data still logged) |
| Concurrent reads | 1 at a time | Single VISA session; Single Read blocked during continuous run |
| Instrument address | Fixed `GPIB0::6::INSTR` | Hardcoded `RESOURCE` constant |
| Overload | Returned as `OL`, plotted as 0 | Range too low for signal |

#### Accuracy & resolution (per mode)

| Mode | Resolution | Accuracy | Status |
|------|-----------|----------|--------|
| DC Voltage | up to 6½ digits (NPLC dep.) | TBD | TBD — needs measurement |
| AC Voltage | TBD | TBD | TBD — needs measurement |
| Resistance | TBD | TBD | TBD — needs measurement |
| Frequency / Period | gate-time dep. (0.01/0.1/1.0 s → 4½/5½/6½ digits) | TBD | TBD — needs measurement |
| Diode | TBD | TBD | TBD — needs measurement |

---

## 3. Requirements / Pre-requisites

### 3.1 Hardware

| Item | Model / Spec | Notes |
|------|--------------|-------|
| Digital multimeter | HP/Agilent **34401A** | 6½-digit bench DMM, GPIB-capable |
| GPIB interface adapter | **NI GPIB-USB-HS** (or equivalent) | USB ↔ GPIB bridge |
| GPIB cable | IEEE-488 cable | Meter ↔ adapter |
| Host PC | Windows 10/11 | Tested with Python 3.10 |
| Test leads / DUT | Probes, diodes, resistors, etc. | Depends on measurement mode |

**Hardware photos:**
- HP 34401A front panel
![HP 34401A front panel](images/image.png)
- NI GPIB-USB-HS adapter
![NI GPIB-USB-HS adapter](images/image-1.png)
- IEEE-488 GPIB cable / connector
![IEEE-488 GPIB cable](images/image-2.png)
- Test leads / probes
![Test leads](images/image-3.png)

### 3.2 Protections (optional)

> Document electrical/operational protections. Confirm hardware-specific values
> against `e9d43e.pdf` before relying on them.

**Instrument input protection (34401A — verify against datasheet)**

| Terminal / Mode | Max input | Status |
|-----------------|-----------|--------|
| Voltage input (HI–LO) | up to 1000 V DC / 750 V AC | TBD — verify |
| Current input (if used) | fused (e.g. 3 A / 250 V) | TBD — verify (current modes not yet in GUI) |
| Input overvoltage cat. | per datasheet | TBD — verify |

**Software / operational protections (implemented)**
- **Overload handling:** `OL` readings are detected and displayed safely (plotted
  as 0, not crashed).
- **Retry on transient faults:** up to 3 retries with buffer clear on VISA errors.
- **Alarm thresholds:** optional low/high limits visually flag out-of-range values.
- **Clean session handling:** background thread opens/closes its own VISA session
  and won't clobber a newer session on restart.

> ⚠️ **Operator safety:** Do not exceed the 34401A's rated input limits. Confirm
> ranges and terminal ratings in the official manual before high-voltage or
> current measurements. Current measurement modes are **not yet implemented** in
> the GUI.

### 3.3 Software Tools

| Tool | Purpose | Where to get it |
|------|---------|-----------------|
| Python 3.10 (Windows) | Runtime for the GUI | https://www.python.org/downloads/ |
| NI-VISA | VISA instrument I/O layer | https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html |
| NI-488.2 | GPIB driver (required for GPIB) | https://www.ni.com/en/support/downloads/drivers/download.ni-488-2.html |
| PyVISA | Python ↔ VISA binding | `pip install pyvisa` — https://pyvisa.readthedocs.io |
| matplotlib | Live trend chart | `pip install matplotlib` — https://matplotlib.org |
| openpyxl | Excel export | `pip install openpyxl` — https://openpyxl.readthedocs.io |

> **NI driver component selection:** During the NI-VISA and NI-488.2 installers,
> install the Runtime, Configuration Support, MAX support, and utilities. You can
> skip the .NET / C/C++ / Visual Basic development components — they are not needed
> for Python use. (See the original `USER_GUIDE.md` for the exact checklist.)

---

## 4. Setup Steps

📷 [IMAGE: Overall setup diagram — PC → USB → GPIB adapter → GPIB cable → 34401A]
*(Will be added later)*

### Step 1 — Configure the multimeter for GPIB
1. Power on the HP 34401A.
2. Press **Shift → I/O Menu**.
3. **2: INTERFACE** → set to `HP-IB / 488`.
4. **1: HP-IB ADDR** → set to `6` (suite default).
5. Connect the GPIB cable between the meter and the NI USB-GPIB adapter, then plug
   the adapter into the PC.

📷 [IMAGE: 34401A I/O menu showing HP-IB and address 6]
*(Will be added later)*

### Step 2 — Install NI drivers
1. Install **NI-VISA** (link in §3.3). Reboot.
2. Install **NI-488.2** (link in §3.3). Reboot.

### Step 3 — Verify the instrument in NI MAX
1. Open **NI MAX** (Measurement & Automation Explorer).
2. Expand **Devices and Interfaces** → confirm `GPIB0` appears.
3. Right-click `GPIB0` → **Scan for Instruments** → confirm the 34401A at
   address `6`.

📷 [IMAGE: NI MAX showing GPIB0 and the detected 34401A]
*(Will be added later)*

### Step 4 — Set up the Python environment
Run in PowerShell from the project folder:

```powershell
cd c:\DAQ-Automation\MultimeterAutomation\MultimeterAutomation
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip pyvisa matplotlib openpyxl
```

> **Note:** The virtual environment must match an installed Python version. If
> `.venv` was built against a Python that is no longer installed, delete and
> rebuild it (`Remove-Item -Recurse -Force .venv` then recreate as above).

### Step 5 — Smoke-test the connection (optional but recommended)

```powershell
.\.venv\Scripts\python.exe import_pyvisa.py
```

Expected output:
```
VISA resources: ('ASRL3::INSTR', 'GPIB0::6::INSTR')
HEWLETT-PACKARD,34401A,0,7-5-2
DC voltage: +2.29700000E-05 V
...
```
Press `Ctrl+C` to stop.

---

## 5. How To Use It

### 🟢 TL;DR — Quick Run
```powershell
cd c:\DAQ-Automation\MultimeterAutomation\MultimeterAutomation
.\.venv\Scripts\python.exe voltage_ui.py
```
Then in the window: pick **Mode** → (optional) **Apply Preset** → **Connect & Start**
→ **Stop** → **Export Excel/CSV**.

> **AI prompts:** N/A — no AI is part of the runtime measurement flow.

### Full step-by-step

1. **Launch the GUI:**
   ```powershell
   cd c:\DAQ-Automation\MultimeterAutomation\MultimeterAutomation
   .\.venv\Scripts\python.exe voltage_ui.py
   ```
   The dark-themed **"HP 34401A Measurement Console"** window opens.

   ![GUI main window](images/image.png)

2. **Choose a measurement mode** from the **Mode** dropdown (DC Voltage, AC
   Voltage, Resistance, Continuity, Diode, Frequency, Period). Controls that don't
   apply to the mode are disabled automatically.

3. **Configure settings (optional):**
   - **Sample interval (s):** time between readings (e.g. 0.2–1.0 s).
   - **NPLC:** integration cycles — lower = faster/noisier, higher = slower/cleaner.
   - **Autozero:** on for best DC/resistance accuracy.
   - **Auto range / Range:** auto, or uncheck and enter a fixed range (e.g. `10`).
   - **Aperture (s):** gate time for Frequency/Period (0.01 / 0.1 / 1.0).
   - **Low/High alarm + Enable alarm:** flags out-of-limit readings in red.

4. **Or apply a Preset:** select one (Fast, Stable Precision, Diode Quick,
   AC Monitor, Frequency Gate) and click **Apply Preset**.

5. **Start acquiring:** click **Connect & Start**. The live value, statistics, and
   trend chart update in real time. Status shows the connected `*IDN?` string.

6. **Single spot check (alternative):** with acquisition stopped, click
   **Single Read** for one reading.

7. **Switch modes on the fly:** changing the Mode dropdown while running clears the
   chart/history, reconfigures the meter, and resumes automatically — no manual
   stop/start needed.

8. **Stop** when done.

9. **Export data:**
   - **Export CSV** → columns `Mode, Timestamp, Reading, Settings`.
   - **Export Excel** → `Readings` sheet + `Chart` sheet with an embedded line
     chart.
   - **Clear Data** resets chart, stats, and history.

   📷 [IMAGE: Example exported Excel with chart]
   *(Will be added later)*

### How you know it's working (pass criteria)
- Status bar shows the connected instrument ID (e.g. `HEWLETT-PACKARD,34401A,...`).
- The large numeric display updates at the configured interval.
- The trend chart scrolls and the Count statistic increments.

### When finished (teardown)
- Click **Stop** to end acquisition and release the VISA session.
- **Export** any data you want to keep, then close the window.

### Example workflows
- **Log a DC rail:** Mode = DC Voltage → Apply preset `Stable Precision` →
  (optional Range = 10) → Connect & Start → Stop → Export Excel.
- **Test a diode:** Mode = Diode → red lead to anode, black to cathode →
  Single Read (~0.55–0.8 V good; reverse leads → `OL`).
- **Check continuity:** Mode = Continuity → Connect & Start → probe two points
  (low Ω = good).
- **Measure frequency:** Mode = Frequency → Aperture = 0.1 → connect signal →
  Connect & Start.

---

## 6. Common Errors

| Error / Symptom | Cause | Fix |
|-----------------|-------|-----|
| `did not find executable at '...Python314\python.exe'` | `.venv` built against a Python version no longer installed | Delete and rebuild `.venv` with an installed Python (see §4 Step 4) |
| `Could not locate a VISA implementation` | NI-VISA not installed | Install NI-VISA, reboot |
| `No module named 'gpib'` / `VI_ERROR_LIBRARY_NFOUND` | NI-488.2 (GPIB driver) missing | Install NI-488.2, reboot |
| `VI_ERROR_TMO` (timeout) | Transient GPIB hiccup | GUI retries up to 3×; reseat cable, lower sample rate if persistent |
| `GPIB0::6::INSTR` not found | Wrong address or meter not in HP-IB mode | Confirm address `6` in NI MAX; check meter I/O settings; update `RESOURCE` if needed |
| UI shows `ERROR` after Start | Address mismatch / meter offline | Verify in NI MAX; confirm cable and power |
| `OL` in display | Signal exceeds active range | Use auto range or a higher fixed range |
| ERR annunciator on meter | Invalid SCPI sequence (legacy) | Current code clears with `*CLS`/`*OPC?`; if seen, restart acquisition |
| Excel export fails | `openpyxl` not installed | `pip install openpyxl` in the venv |
| Normal reading shows red | Alarm enabled with wrong thresholds | Disable alarm or fix low/high values |
| `Permission denied to <user>` on `git push` | Machine credential helper bound to another account | Use SSH with your own key, or clear the cached credential |

📷 [IMAGE: Example error dialog / status bar message]
*(Will be added later)*

---

## 7. Appendix

### 7.1 Open Questions / Next Steps
1. **Characterize sampling rate** (fastest/slowest stable per mode) and record units.
2. **Duration limit test** — find practical max run length; consider streaming to
   disk for long captures instead of holding all readings in memory.
3. **Confirm ranges/accuracy/protection** from `e9d43e.pdf` and replace TBD rows.
4. **Add missing modes** — DC/AC current and 4-wire resistance.
5. **Parameterize the VISA address** (remove hardcoded `GPIB0::6::INSTR`).
6. **Define a headless/API mode** so a test sequencer can drive the block.
7. **Integrate into GTAX.**
8. **Insert all images** marked `📷 [IMAGE: ...]`.

### 7.2 Glossary
| Term | Meaning |
|------|---------|
| DMM | Digital Multimeter |
| GPIB / HP-IB | IEEE-488 instrument bus |
| SCPI | Standard Commands for Programmable Instruments |
| VISA | Virtual Instrument Software Architecture (I/O layer) |
| NPLC | Number of Power-Line Cycles (integration time) |
| Aperture | Gate time for frequency/period measurements |
| `OL` | Overload (signal exceeds active range) |
| DUT | Device Under Test |

### 7.3 Legend
> _TBD — needs measurement_ = obtain empirically; _TBD — needs verification_ =
> expected from datasheet but not yet confirmed.
