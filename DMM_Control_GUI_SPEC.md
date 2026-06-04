# Engineering Specification — DMM Control GUI

**Document type:** Lab-Automation Building Block Specification
**Status:** Draft
**Last updated:** 2026-05-29
**Author:** _TBD_

---

## PART 1 — Mini Spec-let (What & Why)

### 1. Building Block Name
**DMM Control GUI**

### 2. Purpose
A desktop GUI that automates configuration, live acquisition, and logging of
measurements from a bench digital multimeter (DMM) over GPIB. It replaces manual
front-panel button-pushing and hand-recorded readings with a repeatable,
software-driven workflow.

### 3. Why
- Manual DMM logging is slow, error-prone, and not reproducible across operators.
- Long-duration measurements (rail monitoring, drift, thermal soak) require
  unattended, time-stamped capture that the instrument front panel cannot provide.
- A standardized building block lets any teammate run the same measurement the
  same way and export results in a shareable format.

### 4. Inputs
What the user provides or configures in the GUI:

| Input | Description |
|-------|-------------|
| Measurement mode | DC Voltage, AC Voltage, Resistance, Continuity, Diode, Frequency, Period |
| Sample interval (s) | Time between readings (e.g. 0.2–1.0 s) |
| NPLC | Integration time in power-line cycles (DC V / Resistance) |
| Autozero | On/Off (DC V / Resistance) |
| Auto range / fixed range | Let meter pick range, or enter a fixed range value |
| Aperture (s) | Gate time for Frequency / Period |
| Low / High alarm + enable | Threshold limits that flag out-of-range readings |
| Preset | Predefined setting bundle (Fast, Stable Precision, Diode Quick, AC Monitor, Frequency Gate) |

### 5. Outputs
| Output | Description |
|--------|-------------|
| Live numeric display | Current reading with unit, color-coded for alarm state |
| Live trend chart | Reading vs. time (rolling 300-point window) |
| Run statistics | Count, Min, Max, Mean for the active mode |
| CSV export | Columns: `Mode, Timestamp, Reading, Settings` |
| Excel export | `Readings` sheet (formatted) + `Chart` sheet with embedded line chart (`openpyxl`) |

### 6. Dependencies
| Dependency | Detail |
|------------|--------|
| DMM model | HP/Agilent 34401A |
| Connection type | GPIB (IEEE-488) via NI USB-GPIB adapter |
| Instrument driver | NI-VISA + NI-488.2 |
| VISA resource | `GPIB0::6::INSTR` (default GPIB address 6) |
| Language / framework | Python 3.10, Tkinter GUI |
| Python packages | `pyvisa`, `matplotlib` (TkAgg), `openpyxl` |
| Command protocol | SCPI (e.g. `CONF:VOLT:DC`, `READ?`, `*IDN?`) |

### 7. Lego Interface (how it connects to other building blocks)
- **Upstream (control in):** Launched standalone today. Configuration is via the
  GUI; a future headless/API mode could accept a config file or function call so
  a test sequencer can drive it. _(planned — TBD)_
- **Downstream (data out):** Emits standardized CSV/Excel files that other blocks
  (analysis, reporting, pass/fail evaluation) can consume.
- **Instrument bus:** Speaks SCPI over VISA, so the same block can be re-pointed
  at other SCPI DMMs with minimal change to the mode/command table.

---

## PART 2 — Multimeter Capability & Boundaries Spec

### Specifications Summary

| Parameter | Value |
|-----------|-------|
| Device | HP/Agilent 34401A (6½-digit DMM) |
| Interface | GPIB (IEEE-488), NI USB-GPIB adapter |
| Protocol | SCPI over NI-VISA |
| Fastest sampling rate (observed) | TBD — needs measurement |
| Slowest sampling rate (observed) | TBD — needs measurement |
| Max test duration tested | TBD — needs measurement |
| Modes exercised by GUI | DC Voltage, AC Voltage, Resistance, Continuity, Diode, Frequency, Period |
| Accuracy notes | TBD — needs measurement (see datasheet `e9d43e.pdf`) |
| Resolution | Up to 6½ digits (mode/NPLC dependent) — TBD per mode |

### 1. Device
- **Model:** HP/Agilent 34401A, 6½-digit bench digital multimeter.
- **Reference manual:** `e9d43e.pdf` (in workspace).

### 2. Sampling Rate

| Limit | Value | Notes |
|-------|-------|-------|
| Fastest | TBD — needs measurement | GUI floors sample interval logic at 0.5 s default; instrument capable of faster with low NPLC / short aperture |
| Slowest | TBD — needs measurement | Bounded by chosen interval, NPLC, and autozero overhead |

> Note: In this GUI, effective sample rate = software `Sample interval` + instrument
> conversion time (driven by NPLC or Aperture). The hardware reading rate has not
> yet been characterized independently.

### 3. Maximum Test Duration

| Sampling rate | Max duration | Limited by |
|---------------|--------------|------------|
| Fast | TBD — needs measurement | PC RAM (readings held in memory list) |
| Medium | TBD — needs measurement | PC RAM |
| Slow | TBD — needs measurement | PC RAM |

> Note: Readings are accumulated in an in-memory list on the PC (not the
> instrument's reading buffer), so the practical duration limit is host memory and
> chart redraw cost, not instrument storage. Exact limits are TBD.

### 4. Measurement Modes

| Mode | Unit | Range control | NPLC | Autozero | Aperture |
|------|------|---------------|------|----------|----------|
| DC Voltage | V | Yes | Yes | Yes | — |
| AC Voltage | V | Yes | — | — | — |
| Resistance (2-wire) | Ω | Yes | Yes | Yes | — |
| Continuity | Ω | Fixed | — | — | — |
| Diode | V (Vf) | Fixed | — | — | — |
| Frequency | Hz | Yes | — | — | Yes |
| Period | s | Yes | — | — | Yes |

### 5. Measurement Ranges

| Mode | Ranges | Source |
|------|--------|--------|
| DC Voltage | 100 mV, 1 V, 10 V, 100 V, 1000 V | Datasheet — values TBD/confirm |
| AC Voltage | 100 mV – 750 V | Datasheet — values TBD/confirm |
| Resistance | 100 Ω – 100 MΩ | Datasheet — values TBD/confirm |
| Frequency | 3 Hz – 300 kHz | Datasheet — values TBD/confirm |
| Period | corresponding to freq range | Datasheet — values TBD/confirm |
| Continuity | fixed ~1 kΩ range | Datasheet — confirm |
| Diode | fixed ~1 V test | Datasheet — confirm |

> All range values above are from general 34401A knowledge and must be confirmed
> against `e9d43e.pdf`. Mark as **TBD — needs verification.**

### 6. Accuracy & Resolution

| Mode | Resolution (digits) | Accuracy | Status |
|------|---------------------|----------|--------|
| DC Voltage | up to 6½ (NPLC dependent) | TBD — needs measurement | TBD |
| AC Voltage | TBD | TBD — needs measurement | TBD |
| Resistance | TBD | TBD — needs measurement | TBD |
| Frequency | gate-time dependent (0.01 / 0.1 / 1.0 s → 4½ / 5½ / 6½ digits) | TBD — needs measurement | TBD |
| Period | gate-time dependent | TBD — needs measurement | TBD |
| Continuity | n/a (pass/fail) | n/a | — |
| Diode | TBD | TBD — needs measurement | TBD |

### 7. Known Constraints, Edge Cases & Failure Conditions
- **Overload (`OL`):** When a signal exceeds the active range, the meter returns
  an overload; the GUI displays `OL` and plots it as 0. Use auto range or a higher
  fixed range.
- **VISA timeouts:** Occasional GPIB hiccups occur; the read loop retries up to
  3 times (`MAX_RETRIES`) with a buffer clear before surfacing an error.
- **Mode-switch settling:** Function changes issue `*CLS` + `CONF` + `*OPC?` and a
  short delay; switching modes clears chart/history and reconfigures the meter.
- **Single thread to instrument:** Single Read is blocked while continuous
  acquisition is running (one VISA session at a time).
- **Hardcoded address:** Resource is fixed at `GPIB0::6::INSTR`; a different GPIB
  address requires editing `RESOURCE`.
- **Chart window:** Trend chart keeps only the most recent 300 points
  (`MAX_POINTS`); older points scroll off the plot (full data still logged).

### 8. Assumptions & Unverified Items
- Instrument GPIB address is **6**. _(assumption — confirm in NI MAX)_
- NI-VISA and NI-488.2 are installed and the adapter enumerates as `GPIB0`.
  _(confirmed installed per user, 2026-05-29)_
- 34401A range/accuracy figures above are **TBD — needs verification** against
  the datasheet.
- Hardware sampling-rate ceiling and max duration are **TBD — needs measurement.**
- True-RMS bandwidth and crest-factor limits for AC modes are **TBD.**

---

## Open Questions / Next Steps
1. **Characterize sampling rate:** Measure fastest/slowest stable reading rate per
   mode (vary NPLC / aperture) and record units.
2. **Duration limit test:** Run long captures to find practical max duration and
   confirm the host-memory limit; consider streaming-to-disk for long logs.
3. **Confirm ranges & accuracy:** Extract exact range, accuracy, and resolution
   tables from `e9d43e.pdf` and replace the TBD rows.
4. **Lego/automation interface:** Define a headless or API mode (config file or
   function entry point) so the block can be driven by a test sequencer.
5. **Multi-instrument support:** Decide whether to parameterize the VISA resource
   address (remove hardcoded `GPIB0::6::INSTR`).
6. **Verify metadata:** Confirm exact 34401A model variant and firmware via `*IDN?`.

> **Legend:** _TBD — needs measurement_ = value to be obtained empirically;
> _TBD — needs verification_ = value expected from datasheet but not yet confirmed.
