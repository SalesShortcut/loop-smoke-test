---
name: changelog
description: Use when adding, changing or removing any feature in this repository — appends a properly formatted entry to CHANGELOG.md. Trigger on any feature work, plan execution, or public API change.
---

# Changelog

При любом изменении публичного API репозитория добавь запись в `CHANGELOG.md`
(в корне репо) — **одну строку на фичу, строго в этом формате**:

```
- YYYY-MM-DD: <имя функции> — <краткое описание на русском>
```

Правила:

1. Дату бери текущую (UTC).
2. Новые записи добавляются В КОНЕЦ файла (хронологический порядок).
3. Заголовок `# Changelog` в файле уже есть — не дублировать.
4. Запись коммитится вместе с коммитом фичи, а не отдельно.

Пример:

```
- 2026-07-31: slugify — URL-безопасные слаги из произвольных строк
```
