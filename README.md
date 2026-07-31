# loop-smoke-test

Игрушечный репозиторий для смоук-теста loop-orchestrator: библиотека `textkit`
с функциями обработки строк на чистой стандартной библиотеке Python
(без зависимостей — тесты через `unittest`).

```bash
python3 -m unittest discover -s tests -v
```

## slugify

`slugify(text)` превращает произвольную строку в URL-безопасный слаг: только
`a-z`, `0-9` и дефис. Любая последовательность прочих символов (пробелы,
пунктуация) схлопывается в один дефис, крайние дефисы обрезаются.

```python
from textkit import slugify

slugify("Hello, World!")      # "hello-world"
slugify("Python 3.12 rocks")  # "python-3-12-rocks"
slugify("---hello---")        # "hello"
```

Не-ASCII символы не транслитерируются, а считаются разделителями — строка из
одной лишь кириллицы даёт пустой результат:

```python
slugify("  Много   пробелов  ")  # ""
```
