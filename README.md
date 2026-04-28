# ControlMultipleMECG

A Python-based control and data capture system for managing multiple WhaleTeq MECG, synchronizing EEG display capture, and logging session data for EG case replay workflows.

![AdvanceBIS Setup](AdvanceBIS_setup.png)

---

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Pre-Session Checklist](#pre-session-checklist)
- [Channel Mapping and Scaling](#channel-mapping-and-scaling)
- [Troubleshooting](#troubleshooting)

---

## Overview

`Control_Both_MECG.py` automates the full M0 case replay pipeline:

1. **Start Capture** — Initiates BIS Advance and SedLine display capture (video or images at configurable intervals).
2. **Run Case** — Replays the M0 EEG for the full case duration on the chosen EEG system, then stops recordings.
3. **Data Logging** — Uploads raw media to controlled storage using the correct naming convention.

---

## Requirements

- **OS:** Windows (required for Device Manager and DLL support)
- **Python:** 3.x
- **Hardware:**
  - WhaleTeq MECG device(s) (e.g., `WME2101-240xxx`)
  - BIS Advance display + webcam
  - SedLine display + webcam
- **Dependencies:**
  - WhaleTeq SDK (`MECG20x64.dll`, `MECG20x64.2.dll`)  
    Download from: [IEE-352 on Confluence](https://pascallqms.atlassian.net/browse/IEE-352)
  - Python packages: opencv-python, time, threading, zipfile

---

## Installation

1. Clone this repository:
```bash
   git clone https://github.com/your-org/ControlMultipleMECG.git
   cd ControlMultipleMECG
```

2. Install required Python packages:
```bash
   pip install opencv-python time threading zipfile
```

3. To connect additional MECG devices, duplicate the DLL, rename it to `MECG20x64.n.dll`, and pass it to a new `Device` instance (see [Configuration](#configuration)).

---

## Configuration

Before running, update the following variables in `Control_Both_MECG.py`:

| Variable | Description | Example |
|---|---|---|
| `folder` | Path to the directory containing input replay files | `"C:\cases\input"` |
| `cam1_path` | Index of the first webcam | `0` |
| `cam2_path` | Index of the second webcam | `1` |
| `zipResults` | If `True`, saves output as a `.zip` archive in `OUTPUT_ROOT` (requires local disk space) | `True` / `False` |
| `shared_lock` | Pass to `Device.shared_lock` to synchronize case progression across devices | See [Usage](#usage) |

---

## Usage

### Basic Run

```bash
python Control_Both_MECG.py
```

### Running Cases Synchronously Across Devices

To ensure all devices advance to the next unrecorded case together, pass `shared_lock` to each `Device` instance:

```python
device1 = Device("WME2101-240001", dll_path="C:/sdk/MECG20x64.dll", shared_lock=shared_lock)
device2 = Device("WME2101-240002", dll_path="C:/sdk/MECG20x64.2.dll", shared_lock=shared_lock)
```

> **Note:** Any `Device` not instantiated with `shared_lock` will iterate through cases independently.

---

## Pre-Session Checklist

Before each recording session, verify the following:

- [ ] **MECG devices detected** — Each connected device should print:
device is connected (WME2101-240xxx)
- [ ] **Webcams detected** — Each camera should print:
[device_cam] started (x) is_open=True
- [ ] **Output directory is writable** — Confirm `OUTPUT_ROOT` exists and has write permissions. Set `zipResults = True` if a compressed archive is needed.
- [ ] **Replay file verified** — Confirm the selected case replay file exists and matches the intended case ID. On successful start, you should see:
[timestamp], [device] started case x - saving images to your/path
---

## Channel Mapping and Scaling

When using MECG with **Lead I** or **Lead II**, apply Wilson Terminal lead-cancellation and scale channels V1–V6 as appropriate so that the intended differential signals appear correctly at the monitor input.

If using `convert_to_whaleteq_format.py`, this correction is applied **automatically**.

---

## Troubleshooting

| Issue | What to Check |
|---|---|
| MECG device not detected | Verify `device name` string and path to `MECG20x64.dll` / `MECG20x64.2.dll` |
| Webcam not found | Update `cam1_path` / `cam2_path` to correct webcam indices |
| Input files not loading | Ensure `folder` points to the correct input directory |
| Webcam index unknown | Press **Win + X** → **Device Manager** → expand **Imaging Devices** to find connected cameras |
| Output not saving | Confirm `OUTPUT_ROOT` path exists and the current user has write access |

---