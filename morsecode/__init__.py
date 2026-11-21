"""morsecode：零依赖的摩尔斯电码编解码与 A4 练习卡工具。"""

from __future__ import annotations

from .model import (
    DEFAULT_CARDS,
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
from .render import CARDS_PER_PAGE, MAX_TITLE, page_count, render_card_html

__version__ = "0.1.0"

__all__ = [
    "CARDS_PER_PAGE",
    "DEFAULT_CARDS",
    "MAX_CARDS",
    "MAX_TITLE",
    "MIN_CARDS",
    "MORSE_CODE",
    "WORDS",
    "MorseCodeError",
    "decode_morse",
    "encode_text",
    "morse_for",
    "page_count",
    "pick_words",
    "render_card_html",
    "validate",
    "__version__",
]
