# loop-smoke-test

Игрушечный репозиторий для смоук-теста loop-orchestrator: библиотека `textkit`
с функциями обработки строк на чистой стандартной библиотеке Python
(без зависимостей — тесты через `unittest`).

```bash
python3 -m unittest discover -s tests -v
```

## HTTP API

Веб-плейграунд (`python3 -m textkit.web`, порт из `TEXTKIT_PORT`, по умолчанию
3000) отдаёт два JSON-эндпоинта. Все ответы — с заголовком
`Content-Type: application/json; charset=utf-8`.

| запрос | ответ |
| --- | --- |
| `GET /api/transforms` | `200 {"transforms": ["initials", ...]}` — имена преобразований по алфавиту |
| `POST /api/transform` с `{"fn": "<имя>", "text": "<текст>"}` | `200 {"result": "<результат>"}` |
| некорректное тело или неизвестное имя | `400 {"error": "<сообщение>"}` |

Поле `op` принимается как устаревший синоним `fn`; если присутствуют оба,
используется `fn`.

```bash
curl -s 127.0.0.1:3000/api/transforms
curl -s -X POST 127.0.0.1:3000/api/transform -d '{"fn":"slugify","text":"Ada Lovelace"}'
```
