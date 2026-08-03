# Issue #15: feat: title-case transform

Labels: loop:ready

Add a `title_case` transform to textkit and expose it in the web playground.

Requirements:
- New function `title_case(text: str) -> str` in the textkit library: capitalizes the first letter of every word, the rest lowercase. Small connector words (a, an, the, and, or, of, in, on) stay lowercase unless they are the first word.
- A new button in the playground UI that applies the transform to the textarea input, following the pattern of the existing transform buttons. Give the button a stable element id so it is easy to target in e2e tests.
- Unit tests for the new function, including edge cases: empty string, single word, connector word first.

