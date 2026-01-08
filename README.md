# UmbrelOS Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Интеграция для мониторинга и управления вашей системой UmbrelOS из Home Assistant.

## Возможности / Features

- **Мониторинг ресурсов (System Monitoring)**:
  - CPU Usage (Использование ЦП)
  - Memory Usage (Использование памяти — общая и по приложениям)
  - Disk Usage (Использование диска)
  - CPU Temperature (Температура)
  - Uptime (Время работы)
- **Управление (Control)**:
  - Включение/выключение приложений (App Switches)
  - Перезагрузка и выключение системы (Reboot/Shutdown)
- **Обновления (Updates)**:
  - Уведомления об обновлениях umbrelOS и возможность установки прямо из HA.
  - Управление обновлениями приложений.
- **Безопасность (Security)**:
  - Статус 2FA (2FA Enabled status).
- **Хранилище (Storage)**:
  - Автоматическое обнаружение внешних накопителей.

## Установка / Installation

### Вариант 1: HACS (Рекомендуется)
1. Откройте **HACS** в вашем Home Assistant.
2. Нажмите на три точки в верхнем правом углу и выберите **Custom repositories** (Пользовательские репозитории).
3. Вставьте ссылку на этот репозиторий.
4. Выберите категорию **Integration**.
5. Нажмите **Add** и установите "UmbrelOS".
6. Перезагрузите Home Assistant.

### Вариант 2: Вручную
1. Скачайте репозиторий.
2. Скопируйте папку `custom_components/umbrel` в директорию `config/custom_components/` вашего Home Assistant.
3. Перезагрузите Home Assistant.

## Настройка / Configuration

1. Перейдите в **Settings** -> **Devices & Services**.
2. Нажмите **Add Integration**.
3. Найдите **UmbrelOS**.
4. Введите IP-адрес вашего Umbrel (или `umbrel.local`) и пароль.

---
Created with ❤️ for the Umbrel community.
