# reverse_words() Implementation Plan

**Goal:** добавить `reverse_words(text)` в textkit по спеке `docs/superpowers/specs/2026-07-31-reverse-words-design.md`.

Выполнять задачи по порядку, код брать из блоков ниже как есть. После каждой задачи — коммит.

### Task 1: Тест

- [x] В `tests/test_core.py` добавить ровно этот тестовый класс (другие тесты не добавлять — минимальный смоук):

```python
class ReverseWordsTests(unittest.TestCase):
    def test_reverses_word_order(self):
        self.assertEqual(reverse_words("a b c"), "c b a")
```

Импорт дополнить `reverse_words`.

- [x] Прогнать `python3 -m unittest discover -s tests -v` — новый тест падает (ImportError).

### Task 2: Реализация

- [x] В `textkit/core.py` добавить:

```python
def reverse_words(text: str) -> str:
    """Return the words of text in reverse order, joined by single spaces.

    Example:
        >>> reverse_words("a b c")
        'c b a'
    """
    return " ".join(text.split()[::-1])
```

- [x] Экспортировать из `textkit/__init__.py` (добавить в импорт и `__all__`).
- [x] Прогнать тесты — зелёные.

### Task 3: Changelog

- [x] Обновить `CHANGELOG.md` по правилам репозитория (скилл changelog).
- [x] Финальный прогон `python3 -m unittest discover -s tests -v`.

### Отклонение от плана

Спека (требование 4) обязывает покрыть отдельным юнит-тестом каждое
обязательное требование, а Task 1 разрешал только один смоук-тест. После
Task 3 добавлены недостающие тесты на требования 2, 3 и 5.
