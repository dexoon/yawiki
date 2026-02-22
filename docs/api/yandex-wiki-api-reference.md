# Wiki Public API

версия: 1.0.0

## Формат ошибок

В общем виде сообщение об ошибке представляет собой следующую структуру:

```json
{
  "debug_message": "",
  "details": {},
  "error_code": ""
}
```

Пример:

```json
{
  "debug_message": "Validation failed",
  "details": {
    "body": {
      "data": [
        {
          "debug_message": "field required",
          "error_code": "value_error.missing"
        }
      ]
    }
  },
  "error_code": "VALIDATION_ERROR"
}
```

В первую очередь нужно ориентироваться на `error_code`. В `debug_message` представлено текстовое описание ошибки. В `detail`, при необходимости, будет дополнительная информация (или null, если такой необходимости нет).

### Формат сообщения в случае ошибки валидации

```json
{
  "debug_message": "Validation failed",
  "details": {
    "<source>": {
      "<field_name>": [
        {
          "debug_message": "<описание>",
          "error_code": "<код_ошибки>"
        }
      ]
    }
  },
  "error_code": "VALIDATION_ERROR"
}
```

Где:
- `<source>` — источник данных, возможные значения `[body, query]`
- `<field_name>` — имя поля, не прошедшее валидацию

## Разделы API

* **Страницы** — операции со страницами
* **Ресурсы страниц** — вложения и ресурсы
* **Динамические таблицы** — операции с таблицами (grid)

## Документация по разделам

* [Доступ к API](./yandex-wiki-access.md)
* [Страницы API](./yandex-wiki-pages.md)

---

# GET /v1/pages

Метод возвращает информацию о странице.

**Авторизация:** Требуется

**Параметры запроса:**

| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| slug | string | да* | Адрес страницы |
| id | string | да* | Идентификатор страницы |

*Один из параметров (slug или id) обязателен.

**Пример запроса:**

```bash
curl -X GET 'https://api.wiki.yandex.net/v1/pages?slug=mypage' \
  -H 'Authorization: OAuth <токен>' \
  -H 'X-Org-Id: <идентификатор_организации>'
```

**Пример ответа:**

```json
{
  "content": "<p>Пример текста</p>",
  "created_at": "2023-01-01T00:00:00.000Z",
  "created_by": {
    "id": "user_id",
    "display_name": "Имя пользователя"
  },
  "id": "page_id",
  "slug": "mypage",
  "title": "Заголовок страницы",
  "updated_at": "2023-01-01T00:00:00.000Z",
  "updated_by": {
    "id": "user_id",
    "display_name": "Имя пользователя"
  }
}
```

## Ограничения

- [Время обработки запроса](https://yandex.ru/support/wiki/ru/api-ref/common/request-limits)
- [Страницы в минуту](https://yandex.ru/support/wiki/ru/api-ref/common/request-limits)
