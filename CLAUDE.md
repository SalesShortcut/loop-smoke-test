# CLAUDE.md

Правила этого репозитория. Обязательны для любого агента, работающего с кодом.

## Коммиты

- Каждое сообщение коммита ОБЯЗАНО начинаться с префикса `[textkit] `.
  Пример: `[textkit] feat: функция initials`.
- НИКОГДА не коммить артефакты: `__pycache__/`, `*.pyc` (они в .gitignore —
  не обходить).

## Код

- Только стандартная библиотека Python, никаких зависимостей.
- У каждой новой публичной функции docstring ОБЯЗАН содержать секцию
  `Example:` с примером вызова и результата:

  ```python
  def initials(name: str) -> str:
      """Return uppercase initials of a name.

      Example:
          >>> initials("ada lovelace")
          'A.L.'
      """
  ```

- Новые публичные функции экспортируются из `textkit/__init__.py`.

## Changelog

- При добавлении любой фичи следуй скиллу `changelog`
  (`.claude/skills/changelog/SKILL.md`).
