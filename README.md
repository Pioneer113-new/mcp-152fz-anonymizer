# 152-FZ Data Anonymization MCP Server

MCP сервер для автоматического обезличивания персональных данных в соответствии с требованиями 152-ФЗ РФ. Использует Microsoft Presidio и Spacy (модель `ru_core_news_lg`) для поиска и замены чувствительной информации.

## Возможности

- **Поиск сущностей**:
  - ФИО (`PERSON`)
  - Телефонные номера (`PHONE_NUMBER`)
  - Email адреса (`EMAIL_ADDRESS`)
  - Паспорт РФ (`RU_PASSPORT`)
  - ИНН (`RU_INN`)
  - СНИЛС (`RU_SNILS`)
  - Водительские удостоверения (`RU_DRIVER_LICENSE`)
  - Полис ОМС (`RU_OMS`)
  - Гос. номера авто (`RU_VEHICLE_PLATE`)
  - Telegram Chat ID (`TG_CHAT_ID`)
  - Банковские карты (`CREDIT_CARD`)
  - Организации (`ORGANIZATION`) и Локации (`LOCATION`)

- **Инструменты**:
  - `anonymize_text`: Заменяет найденные данные на плейсхолдеры (например, `<PASSPORT_RF>`, `<PERSON>`).
  - `audit_text`: Возвращает отчет о найденных категориях данных без их раскрытия.

## Установка и запуск

### Предварительные требования

- Python 3.10+
- `pip`

### Локальный запуск

1. **Клонируйте репозиторий** (или перейдите в папку проекта):

   ```bash
   cd /path/to/project
   ```

2. **Запустите скрипт установки**:

   ```bash
   ./install.sh
   ```

   Скрипт создаст виртуальное окружение, установит зависимости и скачает модель Spacy.

3. **Запустите сервер**:
   ```bash
   source venv/bin/activate
   mcp run main.py
   ```

### Использование через MCP Inspector (SSH)

Вы можете подключиться к серверу удаленно, используя MCP Inspector.

```bash
npx -y @modelcontextprotocol/inspector ssh user@your_vps_ip "cd /path/to/project && source venv/bin/activate && python main.py"
```

## API Инструментов

### `anonymize_text(text: str) -> str`

Обезличивает входной текст.

**Пример:**
_Input:_ "Меня зовут Иван, мой паспорт 4500 123456."
_Output:_ "Меня зовут <PERSON>, мой паспорт <PASSPORT_RF>."

### `audit_text(text: str) -> str`

Проводит аудит текста и возвращает JSON-строку с найденными сущностями.

**Пример:**
_Input:_ "Звоните +79001234567"
_Output:_ `[{'entity_type': 'PHONE_NUMBER', 'start': 8, 'end': 20, 'score': 0.85}]`

## Разработка

### Запуск тестов

```bash
python test_anonymizer.py
```

### Структура проекта

- `main.py`: Точка входа MCP сервера.
- `analyzer_setup.py`: Конфигурация Presidio Analyzer и кастомных распознавателей.
- `install.sh`: Скрипт автоматической настройки.
