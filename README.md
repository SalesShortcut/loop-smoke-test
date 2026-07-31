# loop-smoke-test

Игрушечный репозиторий для смоук-теста loop-orchestrator: библиотека `textkit`
с функциями обработки строк на чистой стандартной библиотеке Python
(без зависимостей — тесты через `unittest`).

```bash
python3 -m unittest discover -s tests -v
```

## initials

`initials(name)` возвращает инициалы имени: из каждого слова (разделение по
пробелам) берётся первый символ в верхнем регистре, после каждого ставится
точка, всё соединяется без пробелов. Пустая строка и строка из одних пробелов
дают `""`.

```python
>>> from textkit import initials
>>> initials("ada lovelace")
'A.L.'
>>> initials("  Grace   Brewster Murray  Hopper ")
'G.B.M.H.'
>>> initials("")
''
```
