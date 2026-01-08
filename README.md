# UmbrelOS Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Monitor and control your UmbrelOS system directly from Home Assistant.

[🇷🇺 Читать на русском](#umbrelos-интеграция-для-home-assistant)

---

## Features

- **System Monitoring**:
  - CPU Usage, Temperature
  - Memory Usage (Total & Per App)
  - Disk Usage
  - Uptime
- **Control**:
  - Start/Stop Apps (Switches)
  - Reboot/Shutdown System
- **Updates**:
  - UmbrelOS update notifications and installation.
  - App updates management.
- **Security**:
  - 2FA Status monitoring.
- **Storage**:
  - Automatic external drive discovery.

## Installation

### Method 1: HACS (Recommended)
1. Open **HACS** in Home Assistant.
2. Go to **Integrations** > **Three dots (top right)** > **Custom repositories**.
3. Paste this repository URL.
4. Select category **Integration**.
5. Click **Add** and install "UmbrelOS".
6. Restart Home Assistant.

### Method 2: Manual
1. Download the repository.
2. Copy `custom_components/umbrel` folder to your HA `config/custom_components/` directory.
3. Restart Home Assistant.

## Configuration

1. Go to **Settings** -> **Devices & Services**.
2. Click **Add Integration**.
3. Search for **UmbrelOS**.
4. Enter your Umbrel IP (or `umbrel.local`) and password.

---

# UmbrelOS Интеграция для Home Assistant

Интеграция для мониторинга и управления вашей системой UmbrelOS из Home Assistant. Поддерживает **Русский** и **Украинский** языки интерфейса.

## Возможности

- **Мониторинг ресурсов**:
  - Использование ЦП, Температура
  - Использование памяти (Общее и по каждому приложению)
  - Использование диска
  - Время работы (Uptime)
- **Управление**:
  - Включение/выключение приложений (Переключатели)
  - Перезагрузка и выключение системы
- **Обновления**:
  - Уведомления об обновлениях umbrelOS и возможность установки прямо из HA.
  - Управление обновлениями приложений (Кнопка "Установить").
- **Безопасность**:
  - Статус двухфакторной аутентификации (2FA).
- **Хранилище**:
  - Автоматическое обнаружение внешних дисков.

## Установка

### Вариант 1: HACS (Рекомендуется)
1. Откройте **HACS** в вашем Home Assistant.
2. Перейдите в **Integrations** > **Три точки (справа сверху)** > **Custom repositories**.
3. Вставьте ссылку на этот репозиторий.
4. Выберите категорию **Integration**.
5. Нажмите **Add** и установите "UmbrelOS".
6. Перезагрузите Home Assistant.

### Вариант 2: Вручную
1. Скачайте этот репозиторий.
2. Скопируйте папку `custom_components/umbrel` в папку `config/custom_components/` вашего сервера Home Assistant.
3. Перезагрузите Home Assistant.

## Настройка

1. Перейдите в **Настройки** -> **Устройства и службы**.
2. Нажмите **Добавить интеграцию**.
3. Найдите **UmbrelOS**.
4. Введите IP-адрес вашего Umbrel (или `umbrel.local`) и пароль.

---
Created with ❤️ for the Umbrel community.