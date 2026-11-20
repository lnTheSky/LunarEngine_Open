<p align="center">
  <a href="https://t.me/lunaraim2">
    <img src="media/image.png" alt="LunarEngine main interface" width="820">
  </a>
</p>

<p align="center">
  <a href="https://t.me/in_the_skyyy"><img src="https://img.shields.io/badge/%40in__the__skyyy-2AABEE?style=for-the-badge&logo=telegram&logoColor=white" alt="Contact @in_the_skyyy"></a>
  <a href="https://t.me/lunaraim"><img src="https://img.shields.io/badge/%40lunaraim-2548BB?style=for-the-badge&logo=telegram&logoColor=white" alt="LunarAim channel @lunaraim"></a>
  <a href="https://t.me/lunaraim2"><img src="https://img.shields.io/badge/%40lunaraim2-17C3E1?style=for-the-badge&logo=telegram&logoColor=white" alt="LunarAim channel @lunaraim2"></a>
</p>

<h3 align="center">Built with</h3>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python%203.11-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11"></a>
  <a href="https://flet.dev/"><img src="https://img.shields.io/badge/Flet-7B61FF?style=for-the-badge&logo=flutter&logoColor=white" alt="Flet"></a>
  <a href="https://opencv.org/"><img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV"></a>
  <a href="https://pytorch.org/"><img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch"></a>
  <a href="https://github.com/ultralytics/ultralytics"><img src="https://img.shields.io/badge/Ultralytics%20YOLO-111F68?style=for-the-badge&logoColor=white" alt="Ultralytics YOLO"></a>
  <a href="https://onnx.ai/"><img src="https://img.shields.io/badge/ONNX-005CED?style=for-the-badge&logo=onnx&logoColor=white" alt="ONNX"></a>
  <a href="https://pypi.org/project/dxcam/"><img src="https://img.shields.io/badge/DXcam-17202C?style=for-the-badge&logo=windows&logoColor=white" alt="DXcam"></a>
  <a href="https://pypi.org/project/pywin32/"><img src="https://img.shields.io/badge/Win32%20%2F%20pywin32-0078D4?style=for-the-badge&logo=windows&logoColor=white" alt="Win32 and pywin32"></a>
</p>

<details>
<summary>Table of contents</summary>
<br>

- [About this archive](#about-this-archive)
- [What the project explored](#what-the-project-explored)
- [Architecture overview](#architecture-overview)
- [Interface gallery](#interface-gallery)
  - [Main control surface](#main-control-surface)
  - [Loading and activation](#loading-and-activation)
- [Archive status](#archive-status)
- [Repository contents](#repository-contents)
- [License](#license)

</details>

> **Archive notice.** LunarEngine is a historical research snapshot from 2023–2025. It is not a maintained product, not a setup guide, and not intended for practical use or adaptation. The project is preserved for educational review of its architecture, UI, and experimental computer-vision pipeline.

## About this archive

LunarEngine was an experimental Windows desktop application built around a configurable control surface, real-time screen processing, model-assisted detection, and modular input/output experiments.

The repository is intentionally presented as a snapshot of the work rather than a current release. Its original runtime is obsolete, its target environment has changed, and the implementation contains exploratory code, hardcoded assumptions, and incomplete components.

## What the project explored

- **Desktop control surface.** A dark Flet-based UI brought configuration, runtime state, game profiles, input settings, and diagnostics into one interface.
- **Real-time capture.** The screen pipeline used DXcam and Windows capture APIs to feed frames into the processing loop.
- **Computer vision.** OpenCV color segmentation and model-backed detection paths were explored alongside PyTorch, Ultralytics, and ONNX-related tooling.
- **Control logic.** Aim, trigger, prediction, smoothing, PID filtering, and configurable target geometry were developed as separate experimental components.
- **Input experiments.** The code contains Windows input paths, HID/USB abstractions, network-based mouse bridges, and driver-facing placeholders.
- **Configuration and localization.** Per-game configuration snapshots, bindings, locale strings, and runtime feature flags were part of the application model.

## Architecture overview

```mermaid
flowchart TB
    ui["Flet desktop UI"]
    config["Settings + game profiles"]
    runtime["Python runtime"]
    capture["ScreenHandler<br/>DXcam / Win32 capture"]
    vision["Vision pipeline<br/>OpenCV + model inference"]
    models["PyTorch / Ultralytics / ONNX paths"]
    control["Aim + trigger + prediction<br/>PID / smoothing filters"]
    output["Mouse and HID experiments<br/>Win32 / USB / network bridges"]
    support["Localization + audio + process state"]

    ui --> config
    ui --> runtime
    config --> runtime
    runtime --> capture
    capture --> vision
    models --> vision
    vision --> control
    control --> output
    runtime --> support

    classDef core fill:#17202c,color:#ffffff,stroke:#00b8d4,stroke-width:2px
    classDef module fill:#243247,color:#ffffff,stroke:#ff5f3d
    classDef support fill:#334155,color:#ffffff,stroke:#a855f7

    class ui,config,runtime core
    class capture,vision,models,control,output module
    class support support
```

## Interface gallery

The archived UI reflects the project’s focus on runtime visibility and dense configuration. The screenshots are preserved as visual documentation, not as a promise of current compatibility.

### Main control surface

<p align="center">
  <img src="media/image.png" alt="LunarEngine main control surface" width="820">
</p>

The main surface combines game and configuration selection, activation state, control actions, runtime metrics, and navigation across the project’s feature areas.

### Loading and activation

<p align="center">
  <img src="media/image2.png" alt="LunarEngine loading and activation screen" width="48%">
</p>

The loading screen documents the application’s startup flow and activation feedback in the archived build.

## Archive status

This repository is **read-only in spirit** and exists as a historical reference.

- The original README states that the code no longer works with current game versions.
- No supported installation or runtime workflow is provided.
- The code was written for Python 3.11 and contains no maintained test suite.
- Several components are intentionally incomplete or excluded, including the real external mouse-driver implementation.
- Do not use this archive to modify games, bypass protections, build cheats, or adapt the code for current software.

## Repository contents

<details>
<summary>Explore the archived source areas</summary>
<br>

- `app_main.py`, `naim_*.py` — Flet application shell, navigation, settings, and loading flow.
- `screen_handler.py`, `predictor.py` — frame capture and detection pipeline.
- `aim.py`, `aim_mouse.py`, `mouse_filter.py` — experimental control, smoothing, and mouse coordination.
- `color_boundings.py`, `compiler.py` — color segmentation and model/runtime loading paths.
- `configs/` — historical per-game and feature configuration snapshots.
- `locales.py`, `media/`, `logo.png` — localization and interface assets.
- `requirements.txt` — archived dependency inventory.

</details>

## License

This project is distributed under the [MIT License](LICENSE). The archive should be read together with the project’s safety notice and attribution requirements.

<br>

<div align="center">
  <img src="logo.png" alt="LunarEngine logo" width="96">
  <h2>LunarEngine</h2>
  <sub>Historical Windows research snapshot · 2023–2025</sub>
</div>
