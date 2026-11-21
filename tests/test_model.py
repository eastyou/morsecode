"""model 模块单元测试：编码表、编解码、校验与抽题。"""

from __future__ import annotations

import unittest

from morsecode.model import (
    MAX_CARDS,
    MIN_CARDS,
    MORSE_CODE,
    WORDS,
    MorseCodeError,
    decode_morse,
    encode_text,
    morse_for,
    pick_words,
    validate,
)

LETTERS = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
}

DIGITS = {
    "0": "-----",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
}

PUNCTUATION = {
    ".": ".-.-.-",
    ",": "--..--",
    "?": "..--..",
    "/": "-..-.",
    "=": "-...-",
    "+": ".-.-.",
    "-": "-....-",
    "(": "-.--.",
    ")": "-.--.-",
    ":": "---...",
    "'": ".----.",
    '"': ".-..-.",
    "@": ".--.-.",
}


class EncodeTest(unittest.TestCase):
    def test_letters(self) -> None:
        for char, code in LETTERS.items():
            self.assertEqual(encode_text(char), code, char)

    def test_lowercase_equals_uppercase(self) -> None:
        self.assertEqual(encode_text("sos"), encode_text("SOS"))
        self.assertEqual(encode_text("hello"), ".... . .-.. .-.. ---")

    def test_digits(self) -> None:
        for char, code in DIGITS.items():
            self.assertEqual(encode_text(char), code, char)

    def test_punctuation(self) -> None:
        for char, code in PUNCTUATION.items():
            self.assertEqual(encode_text(char), code, char)

    def test_sos_2026(self) -> None:
        self.assertEqual(
            encode_text("SOS 2026"), "... --- ... / ..--- ----- ..--- -...."
        )

    def test_word_separator(self) -> None:
        self.assertEqual(
            encode_text("HELLO WORLD"),
            ".... . .-.. .-.. --- / .-- --- .-. .-.. -..",
        )

    def test_multiple_spaces(self) -> None:
        self.assertEqual(
            encode_text("SOS   2026"), "... --- ... / ..--- ----- ..--- -...."
        )

    def test_newlines_and_tabs(self) -> None:
        self.assertEqual(
            encode_text("SOS\n2026\tOK"), "... --- ... / ..--- ----- ..--- -.... / --- -.-"
        )

    def test_leading_trailing_space(self) -> None:
        self.assertEqual(encode_text("  SOS  "), "... --- ...")

    def test_slash_is_encodable_character(self) -> None:
        self.assertEqual(encode_text("A/B"), ".- -..-. -...")

    def test_empty(self) -> None:
        with self.assertRaises(MorseCodeError):
            encode_text("")

    def test_whitespace_only(self) -> None:
        with self.assertRaises(MorseCodeError):
            encode_text(" \n\t ")

    def test_non_text(self) -> None:
        with self.assertRaises(MorseCodeError):
            encode_text(123)  # type: ignore[arg-type]

    def test_chinese_error_points_to_position(self) -> None:
        with self.assertRaises(MorseCodeError) as ctx:
            encode_text("SOS中")
        message = str(ctx.exception)
        self.assertIn("中", message)
        self.assertIn("4", message)

    def test_unsupported_symbol_error(self) -> None:
        with self.assertRaises(MorseCodeError) as ctx:
            encode_text("A#B")
        message = str(ctx.exception)
        self.assertIn("#", message)
        self.assertIn("2", message)

    def test_underscore_rejected(self) -> None:
        with self.assertRaises(MorseCodeError):
            encode_text("A_B")


class DecodeTest(unittest.TestCase):
    def test_letters(self) -> None:
        for char, code in LETTERS.items():
            self.assertEqual(decode_morse(code), char)

    def test_digits(self) -> None:
        for char, code in DIGITS.items():
            self.assertEqual(decode_morse(code), char)

    def test_punctuation(self) -> None:
        for char, code in PUNCTUATION.items():
            self.assertEqual(decode_morse(code), char)

    def test_sentence(self) -> None:
        self.assertEqual(
            decode_morse("... --- ... / ..--- ----- ..--- -...."), "SOS 2026"
        )

    def test_multiple_spaces(self) -> None:
        self.assertEqual(decode_morse("  ...   ---  "), "SO")

    def test_word_separator(self) -> None:
        self.assertEqual(decode_morse("... --- ... / -.-"), "SOS K")

    def test_non_text(self) -> None:
        with self.assertRaises(MorseCodeError):
            decode_morse(123)  # type: ignore[arg-type]

    def test_empty(self) -> None:
        with self.assertRaises(MorseCodeError):
            decode_morse("")

    def test_whitespace_only(self) -> None:
        with self.assertRaises(MorseCodeError):
            decode_morse("   \n ")

    def test_invalid_token_position(self) -> None:
        with self.assertRaises(MorseCodeError) as ctx:
            decode_morse("... --- xyz")
        message = str(ctx.exception)
        self.assertIn("xyz", message)
        self.assertIn("3", message)

    def test_letter_with_slash_inside(self) -> None:
        with self.assertRaises(MorseCodeError) as ctx:
            decode_morse("...-/")
        self.assertIn("...-/", str(ctx.exception))

    def test_leading_slash(self) -> None:
        with self.assertRaises(MorseCodeError):
            decode_morse("/ ...")

    def test_trailing_slash(self) -> None:
        with self.assertRaises(MorseCodeError):
            decode_morse("... /")

    def test_double_slash(self) -> None:
        with self.assertRaises(MorseCodeError):
            decode_morse("... / / ---")

    def test_slash_only(self) -> None:
        with self.assertRaises(MorseCodeError):
            decode_morse("/")


class RoundTripTest(unittest.TestCase):
    def test_all_characters(self) -> None:
        alphabet = "".join(LETTERS) + "".join(DIGITS) + "".join(PUNCTUATION)
        self.assertEqual(decode_morse(encode_text(alphabet)), alphabet)

    def test_words(self) -> None:
        text = "HELLO WORLD 2026"
        self.assertEqual(decode_morse(encode_text(text)), text)

    def test_lowercase_normalizes(self) -> None:
        self.assertEqual(decode_morse(encode_text("hello 2026")), "HELLO 2026")


class ValidateTest(unittest.TestCase):
    def test_valid_text(self) -> None:
        self.assertEqual(validate("SOS 2026"), [])

    def test_text_positions(self) -> None:
        self.assertEqual(validate("SOS中"), [(4, "中")])
        self.assertEqual(validate("中文"), [(1, "中"), (2, "文")])

    def test_valid_morse(self) -> None:
        self.assertEqual(validate("... --- ... / -.-", morse=True), [])

    def test_morse_positions(self) -> None:
        self.assertEqual(validate("... --- xyz", morse=True), [(3, "xyz")])

    def test_morse_slash_ignored(self) -> None:
        self.assertEqual(validate("/ ...", morse=True), [])

    def test_non_text(self) -> None:
        with self.assertRaises(MorseCodeError):
            validate(None)  # type: ignore[arg-type]

    def test_non_bool_flag(self) -> None:
        with self.assertRaises(MorseCodeError):
            validate("SOS", morse=1)  # type: ignore[arg-type]


class PickWordsTest(unittest.TestCase):
    def test_count(self) -> None:
        self.assertEqual(len(pick_words(6, seed=1)), 6)
        self.assertEqual(len(pick_words(MAX_CARDS, seed=1)), MAX_CARDS)

    def test_seed_reproducible(self) -> None:
        self.assertEqual(pick_words(12, seed=42), pick_words(12, seed=42))

    def test_different_seed(self) -> None:
        self.assertNotEqual(pick_words(12, seed=42), pick_words(12, seed=7))

    def test_unique_words(self) -> None:
        words = pick_words(MAX_CARDS, seed=3)
        self.assertEqual(len(set(words)), len(words))

    def test_bounds(self) -> None:
        for count in (MIN_CARDS - 1, MAX_CARDS + 1, 0, -1):
            with self.subTest(count=count):
                with self.assertRaises(MorseCodeError):
                    pick_words(count)

    def test_bad_type(self) -> None:
        for count in (True, "12", 12.0):
            with self.subTest(count=count):
                with self.assertRaises(MorseCodeError):
                    pick_words(count)  # type: ignore[arg-type]

    def test_bad_seed(self) -> None:
        with self.assertRaises(MorseCodeError):
            pick_words(6, seed="42")  # type: ignore[arg-type]
        with self.assertRaises(MorseCodeError):
            pick_words(6, seed=True)

    def test_word_table(self) -> None:
        self.assertGreaterEqual(len(WORDS), MIN_CARDS)
        self.assertEqual(len(set(WORDS)), len(WORDS))
        for word in WORDS:
            self.assertRegex(word, r"^[A-Z]+$")
            self.assertNotIn(word, ("",))

    def test_every_word_roundtrips(self) -> None:
        for word in WORDS:
            self.assertEqual(decode_morse(encode_text(word)), word)


class MorseForTest(unittest.TestCase):
    def test_basic(self) -> None:
        self.assertEqual(morse_for("HELLO"), ".... . .-.. .-.. ---")

    def test_lowercase(self) -> None:
        self.assertEqual(morse_for("hello"), ".... . .-.. .-.. ---")

    def test_strip(self) -> None:
        self.assertEqual(morse_for("  SOS  "), "... --- ...")

    def test_empty(self) -> None:
        with self.assertRaises(MorseCodeError):
            morse_for("  ")

    def test_non_text(self) -> None:
        with self.assertRaises(MorseCodeError):
            morse_for(1)  # type: ignore[arg-type]

    def test_inner_space(self) -> None:
        with self.assertRaises(MorseCodeError):
            morse_for("A B")

    def test_unsupported(self) -> None:
        with self.assertRaises(MorseCodeError) as ctx:
            morse_for("A中")
        self.assertIn("中", str(ctx.exception))


class MorseTableTest(unittest.TestCase):
    def test_expected_entries(self) -> None:
        for char, code in LETTERS.items():
            self.assertEqual(MORSE_CODE[char], code, char)
        for char, code in DIGITS.items():
            self.assertEqual(MORSE_CODE[char], code, char)
        for char, code in PUNCTUATION.items():
            self.assertEqual(MORSE_CODE[char], code, char)


if __name__ == "__main__":
    unittest.main()
