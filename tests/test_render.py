"""render 模块单元测试：A4 练习卡结构、转义与页数。"""

from __future__ import annotations

import unittest

from morsecode.model import MAX_CARDS, MorseCodeError, morse_for, pick_words
from morsecode.render import (
    CARDS_PER_PAGE,
    MAX_TITLE,
    page_count,
    render_card_html,
)

WORDS_12 = list(pick_words(12, seed=42))


class RenderDocumentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.page = render_card_html(WORDS_12)

    def test_doctype_and_language(self) -> None:
        self.assertTrue(self.page.startswith("<!doctype html>"))
        self.assertIn('<html lang="zh-CN">', self.page)
        self.assertIn('<meta charset="utf-8">', self.page)

    def test_a4_portrait(self) -> None:
        self.assertIn("A4 portrait", self.page)
        self.assertIn("size: A4 portrait", self.page)

    def test_viewport(self) -> None:
        self.assertIn('name="viewport"', self.page)

    def test_self_contained(self) -> None:
        lowered = self.page.lower()
        self.assertNotIn("<script", lowered)
        self.assertNotIn("http://", lowered)
        self.assertNotIn("https://", lowered)
        self.assertNotIn(" src=", lowered)
        self.assertNotIn("@import", lowered)

    def test_print_rules(self) -> None:
        self.assertIn("page-break-after: always", self.page)
        self.assertIn("@media print", self.page)

    def test_responsive_rules(self) -> None:
        self.assertIn("@media screen", self.page)
        self.assertIn("max-width: 100%", self.page)

    def test_title(self) -> None:
        self.assertIn("<title>摩尔斯练习卡</title>", self.page)
        self.assertIn("<h1>摩尔斯练习卡</h1>", self.page)

    def test_cards_per_page(self) -> None:
        self.assertEqual(CARDS_PER_PAGE, 3)

    def test_card_count(self) -> None:
        self.assertEqual(self.page.count('<article class="card">'), 12)

    def test_card_sheet_count(self) -> None:
        self.assertEqual(self.page.count('<section class="sheet">'), 4)

    def test_answer_sheet(self) -> None:
        self.assertIn('<section class="sheet answer-sheet">', self.page)
        self.assertIn("参考答案", self.page)
        self.assertEqual(self.page.count("<li>"), 12)

    def test_page_numbers(self) -> None:
        self.assertIn("第 1 / 4 页", self.page)
        self.assertIn("第 4 / 4 页", self.page)

    def test_card_numbers(self) -> None:
        self.assertIn('<span class="no">01</span>', self.page)
        self.assertIn('<span class="no">12</span>', self.page)

    def test_answer_codes(self) -> None:
        for word in WORDS_12:
            self.assertIn(morse_for(word), self.page)

    def test_toolbar_summary(self) -> None:
        self.assertIn("共 12 题", self.page)


class RenderContentTest(unittest.TestCase):
    def test_words_uppercased(self) -> None:
        page = render_card_html(["hello", "World"])
        self.assertIn("HELLO", page)
        self.assertIn("WORLD", page)
        self.assertNotIn("hello", page)

    def test_title_escaped(self) -> None:
        page = render_card_html(["SOS"], title="<练习>")
        self.assertIn("&lt;练习&gt;", page)
        self.assertNotIn("<title><练习></title>", page)

    def test_partial_last_page(self) -> None:
        page = render_card_html(list(pick_words(7, seed=1)))
        self.assertEqual(page.count('<article class="card">'), 7)
        self.assertEqual(page.count('<section class="sheet">'), 3)
        self.assertIn("第 3 / 3 页", page)

    def test_answer_page_contains_every_word(self) -> None:
        words = list(pick_words(6, seed=2))
        page = render_card_html(words)
        for word in words:
            self.assertIn(word, page)


class ValidationTest(unittest.TestCase):
    def test_empty_words(self) -> None:
        with self.assertRaises(MorseCodeError):
            render_card_html([])

    def test_single_string(self) -> None:
        with self.assertRaises(MorseCodeError):
            render_card_html("HELLO")  # type: ignore[arg-type]

    def test_non_sequence(self) -> None:
        with self.assertRaises(MorseCodeError):
            render_card_html(42)  # type: ignore[arg-type]

    def test_too_many_words(self) -> None:
        with self.assertRaises(MorseCodeError):
            render_card_html(["SOS"] * (MAX_CARDS + 1))

    def test_empty_word(self) -> None:
        with self.assertRaises(MorseCodeError):
            render_card_html(["SOS", "  "])

    def test_non_text_word(self) -> None:
        with self.assertRaises(MorseCodeError):
            render_card_html([1])  # type: ignore[list-item]

    def test_word_with_space(self) -> None:
        with self.assertRaises(MorseCodeError):
            render_card_html(["SOS K"])

    def test_unsupported_word(self) -> None:
        with self.assertRaises(MorseCodeError) as ctx:
            render_card_html(["HELLO!"])
        self.assertIn("HELLO!", str(ctx.exception))

    def test_chinese_word(self) -> None:
        with self.assertRaises(MorseCodeError) as ctx:
            render_card_html(["你好"])
        message = str(ctx.exception)
        self.assertIn("你", message)
        self.assertIn("1", message)

    def test_empty_title(self) -> None:
        with self.assertRaises(MorseCodeError):
            render_card_html(["SOS"], title="  ")

    def test_non_text_title(self) -> None:
        with self.assertRaises(MorseCodeError):
            render_card_html(["SOS"], title=1)  # type: ignore[arg-type]

    def test_long_title(self) -> None:
        with self.assertRaises(MorseCodeError):
            render_card_html(["SOS"], title="题" * (MAX_TITLE + 1))


class PageCountTest(unittest.TestCase):
    def test_values(self) -> None:
        cases = {1: 1, 2: 1, 3: 1, 4: 2, 6: 2, 7: 3, 12: 4, 30: 10}
        for words, expected in cases.items():
            self.assertEqual(page_count(words), expected, words)

    def test_bad_values(self) -> None:
        for value in (0, -1, MAX_CARDS + 1, True, "12"):
            with self.subTest(value=value):
                with self.assertRaises(MorseCodeError):
                    page_count(value)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
