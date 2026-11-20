<p align="center">
  <a href="https://t.me/lunaraim2">
    <img src="media/image.png" alt="Главный интерфейс LunarEngine" width="820">
  </a>
</p>

<p align="center">
  <a href="https://t.me/in_the_skyyy"><img src="https://img.shields.io/badge/%40in__the__skyyy-2AABEE?style=for-the-badge&logo=telegram&logoColor=white" alt="Связаться с @in_the_skyyy"></a>
  <a href="https://t.me/lunaraim"><img src="https://img.shields.io/badge/%40lunaraim-2548BB?style=for-the-badge&logo=telegram&logoColor=white" alt="Канал LunarAim @lunaraim"></a>
  <a href="https://t.me/lunaraim2"><img src="https://img.shields.io/badge/%40lunaraim2-17C3E1?style=for-the-badge&logo=telegram&logoColor=white" alt="Канал LunarAim @lunaraim2"></a>
</p>

<p align="center"><a href="README.md">English</a> · <a href="README.ru-RU.md">Русский</a> · <a href="README.zh-CN.md">简体中文</a></p>

<h3 align="center">Создано с помощью</h3>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python%203.11-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11"></a>
  <a href="https://flet.dev/"><img src="https://img.shields.io/badge/Flet-7B61FF?style=for-the-badge&logo=flutter&logoColor=white" alt="Flet"></a>
  <a href="https://opencv.org/"><img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV"></a>
  <a href="https://pytorch.org/"><img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch"></a>
  <a href="https://github.com/ultralytics/ultralytics"><img src="https://img.shields.io/badge/Ultralytics%20YOLO-111F68?style=for-the-badge&logoColor=white" alt="Ultralytics YOLO"></a>
  <a href="https://onnx.ai/"><img src="https://img.shields.io/badge/ONNX-005CED?style=for-the-badge&logo=onnx&logoColor=white" alt="ONNX"></a>
  <a href="https://pypi.org/project/dxcam/"><img src="https://img.shields.io/badge/DXcam-17202C?style=for-the-badge&logo=windows&logoColor=white" alt="DXcam"></a>
  <a href="https://pypi.org/project/pywin32/"><img src="https://img.shields.io/badge/Win32%20%2F%20pywin32-0078D4?style=for-the-badge&logo=windows&logoColor=white" alt="Win32 и pywin32"></a>
</p>

<details>
<summary>Содержание</summary>
<br>

- [Об архиве](#об-архиве)
- [Что исследовал проект](#что-исследовал-проект)
- [Обзор архитектуры](#обзор-архитектуры)
- [Галерея интерфейса](#галерея-интерфейса)
  - [Главная панель управления](#главная-панель-управления)
  - [Загрузка и активация](#загрузка-и-активация)
- [Статус архива](#статус-архива)
- [Содержимое репозитория](#содержимое-репозитория)
- [Лицензия](#лицензия)

</details>

> **Уведомление об архиве.** LunarEngine — исторический research snapshot 2023–2025 годов. Это не поддерживаемый продукт, не инструкция по запуску и не проект для практического использования или адаптации. Репозиторий сохранён для образовательного изучения архитектуры, UI и экспериментального computer-vision pipeline.

## Об архиве

LunarEngine — экспериментальное Windows-приложение с настраиваемой панелью управления, обработкой экрана в реальном времени, model-assisted detection и модульными экспериментами с вводом/выводом.

Репозиторий намеренно представлен как snapshot работы, а не как текущий release. Исходный runtime устарел, целевая среда изменилась, а реализация содержит экспериментальный код, hardcode и незавершённые компоненты.

## Что исследовал проект

- **Desktop control surface.** Тёмный UI на Flet объединял конфигурацию, состояние runtime, игровые профили, настройки ввода и диагностику.
- **Real-time capture.** Pipeline использовал DXcam и Windows capture API для передачи кадров в обработку.
- **Computer vision.** Исследовались OpenCV color segmentation и model-backed detection с PyTorch, Ultralytics и инструментами ONNX.
- **Control logic.** Aim, trigger, prediction, smoothing, PID-фильтрация и настраиваемая геометрия целей развивались как отдельные экспериментальные компоненты.
- **Input experiments.** Код содержит Windows input paths, HID/USB-абстракции, сетевые mouse bridges и placeholders для driver-интеграций.
- **Configuration and localization.** В модель приложения входили игровые конфиги, bindings, locale strings и runtime feature flags.

## Обзор архитектуры

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

## Галерея интерфейса

Архивный UI отражает фокус проекта на наблюдаемости runtime и плотной конфигурации. Снимки сохранены как визуальная документация, а не как обещание совместимости с текущим ПО.

### Главная панель управления

<p align="center">
  <img src="media/image.png" alt="Главная панель управления LunarEngine" width="820">
</p>

Главная панель объединяет выбор игры и конфигурации, статус активации, управляющие действия, runtime-метрики и навигацию по функциональным разделам проекта.

### Загрузка и активация

<p align="center">
  <img src="media/image2.png" alt="Экран загрузки и активации LunarEngine" width="48%">
</p>

Экран загрузки показывает startup flow приложения и feedback активации в архивной сборке.

## Статус архива

Репозиторий существует как исторический reference и по смыслу является **read-only**.

- Исходный README указывает, что код больше не работает с актуальными версиями игр.
- Поддерживаемый workflow установки и запуска не предоставляется.
- Код написан для Python 3.11 и не содержит поддерживаемого test suite.
- Некоторые компоненты намеренно незавершены или исключены, включая настоящую реализацию внешнего mouse driver.
- Не используйте архив для модификации игр, обхода защит, создания читов или адаптации под современное ПО.

## Содержимое репозитория

<details>
<summary>Архивные области исходников</summary>
<br>

- `app_main.py`, `naim_*.py` — Flet shell приложения, навигация, настройки и loading flow.
- `screen_handler.py`, `predictor.py` — pipeline захвата кадров и детекции.
- `aim.py`, `aim_mouse.py`, `mouse_filter.py` — экспериментальные control, smoothing и координация мыши.
- `color_boundings.py`, `compiler.py` — color segmentation и пути загрузки моделей/runtime.
- `configs/` — исторические конфигурации игр и функций.
- `locales.py`, `media/`, `logo.png` — локализация и UI-материалы.
- `requirements.txt` — архивный список зависимостей.

</details>

## Лицензия

Проект распространяется под [MIT License](LICENSE). Архив следует рассматривать вместе с уведомлением о безопасности и требованиями к атрибуции.

<br>

<div align="center">
  <img src="logo.png" alt="Логотип LunarEngine" width="96">
  <h2>LunarEngine</h2>
  <sub>Исторический Windows research snapshot · 2023–2025</sub>
</div>
