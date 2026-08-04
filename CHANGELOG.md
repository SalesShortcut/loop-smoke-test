# Changelog

- 2026-08-01: slugify — URL-безопасные слаги из произвольных строк
- 2026-08-01: shout — текст в верхнем регистре
- 2026-08-01: initials — инициалы имени через точку
- 2026-08-01: reverse_words — обратный порядок слов в строке
- 2026-08-01: truncate — обрезка текста до заданной ширины с «...»
- 2026-08-01: transform — диспетчер операций веб-плейграунда по имени
- 2026-08-01: handle_transform — обработка тела POST /api/transform (200 или 400)
- 2026-08-01: render_page — HTML-страница веб-плейграунда
- 2026-08-01: serve — запуск веб-плейграунда (python3 -m textkit.web)
- 2026-08-01: render_page (Clear) — кнопка Clear очищает поле ввода и результат
- 2026-08-03: render_page (charcount) — живой счётчик символов под полем ввода
- 2026-08-03: render_page (result placeholder) — область результата показывает «Nothing yet» до первого преобразования и после Clear
- 2026-08-03: render_page (result placeholder) — текст плейсхолдера изменён на «Type something and press Apply Beza» по фидбеку ревьюера
- 2026-08-03: render_page (footer) — футер «textkit playground · N operations» с числом операций внизу страницы
- 2026-08-03: title_case — заглавные буквы в словах, служебные слова строчными
- 2026-08-03: handle_transform (fn) — POST /api/transform принимает поле fn (op — устаревший синоним)
- 2026-08-03: list_transforms — GET /api/transforms отдаёт отсортированный список преобразований
- 2026-08-04: snake_case — идентификатор в snake_case из произвольной строки
