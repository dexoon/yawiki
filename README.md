# Yandex Wiki MCP Server

MCP-сервер для работы с Yandex Wiki через Model Context Protocol.

## Установка

### Через uvx (рекомендуется)

```bash
uvx --from git+https://github.com/dexoon/yawiki yawiki
```

### Локальная установка

```bash
git clone https://github.com/dexoon/yawiki.git
cd yawiki
uv sync
```

## Настройка

Создайте файл `.env` или установите переменные окружения:

```env
YANDEX_WIKI_TOKEN=your_oauth_token
YANDEX_TRACKER_ORG_ID=your_org_id
YANDEX_WIKI_BASE_SLUG=users/your_username
```

### Получение токена

1. Перейдите на [oauth.yandex.ru](https://oauth.yandex.ru/)
2. Авторизуйтесь и получите OAuth-токен
3. `YANDEX_TRACKER_ORG_ID` можно найти в настройках Yandex Tracker

## Использование

### Запуск MCP-сервера

```bash
uvx yawiki
```

### Конфигурация для Claude Desktop

Добавьте в `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "yandex-wiki": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/dexoon/yawiki", "yawiki"],
      "env": {
        "YANDEX_WIKI_TOKEN": "your_token",
        "YANDEX_TRACKER_ORG_ID": "your_org_id",
        "YANDEX_WIKI_BASE_SLUG": "users/your_username"
      }
    }
  }
}
```

## Доступные инструменты

| Инструмент | Описание |
|------------|----------|
| `wiki_create` | Создать новую страницу |
| `wiki_read` | Прочитать страницу |
| `wiki_update` | Обновить страницу |
| `wiki_delete` | Удалить страницу |
| `wiki_exists` | Проверить существование страницы |
| `wiki_get_or_create` | Получить или создать страницу |

### Примеры использования

```python
# Создание страницы
wiki_create("scenarios/test", "Тестовая страница", "# Содержание")

# Чтение страницы
wiki_read("scenarios/test")

# Обновление страницы
wiki_update("scenarios/test", content="Новое содержание")

# Проверка существования
wiki_exists("scenarios/test")

# Удаление
wiki_delete("scenarios/test")
```

## CLI

Для прямого использования без MCP:

```bash
yawiki-cli create scenarios/test "Заголовок" -c "# Контент"
yawiki-cli read scenarios/test
yawiki-cli update scenarios/test -c "Новый контент"
yawiki-cli delete scenarios/test
yawiki-cli exists scenarios/test
```

## Разработка

```bash
# Установка зависимостей для разработки
uv sync

# Запуск сервера
uv run yawiki

# Запуск CLI
uv run yawiki-cli --help
```

## Лицензия

MIT
