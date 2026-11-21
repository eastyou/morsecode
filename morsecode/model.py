"""摩尔斯电码模型：编码表、编解码与练习单词抽取。"""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Tuple

MIN_CARDS = 6
MAX_CARDS = 30
DEFAULT_CARDS = 12


class MorseCodeError(ValueError):
    """输入的文本、电码或参数不合法。"""


MORSE_CODE: Dict[str, str] = {
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

_MORSE_TO_CHAR: Dict[str, str] = {code: char for char, code in MORSE_CODE.items()}
_SLASH = "/"

WORDS: Tuple[str, ...] = (
    "APPLE",
    "AUTUMN",
    "BANANA",
    "BREAD",
    "BRIDGE",
    "CAMERA",
    "CASTLE",
    "CHAIR",
    "CLOCK",
    "CODE",
    "COFFEE",
    "COMPUTER",
    "DOLPHIN",
    "DRAGON",
    "DREAM",
    "EAGLE",
    "EMAIL",
    "FAMILY",
    "FOREST",
    "FRIEND",
    "GARDEN",
    "GUITAR",
    "HAPPY",
    "HELLO",
    "ISLAND",
    "KEYBOARD",
    "LETTER",
    "LIGHT",
    "MAGIC",
    "MARKET",
    "MONEY",
    "MORSE",
    "MOUNTAIN",
    "MOUSE",
    "MUSIC",
    "NUMBER",
    "OCEAN",
    "ORANGE",
    "PANDA",
    "PAPER",
    "PENCIL",
    "PHONE",
    "PLANET",
    "PROGRAM",
    "PUZZLE",
    "RADIO",
    "RIVER",
    "ROBOT",
    "ROCKET",
    "SCHOOL",
    "SCIENCE",
    "SCREEN",
    "SIGNAL",
    "SMILE",
    "SOUND",
    "SPORT",
    "SPRING",
    "STUDENT",
    "SUMMER",
    "TEACHER",
    "TIGER",
    "TRAVEL",
    "WATER",
    "WINDOW",
    "WINTER",
    "WORLD",
)


def validate(text: str, morse: bool = False) -> List[Tuple[int, str]]:
    """返回不合法字符或码元及位置（位置从 1 开始）。

    - 文本模式：空白跳过，返回不支持的字符，位置按原文本字符序号。
    - 电码模式：按空白切分，返回无法识别的码元，位置按码元序号。
    """
    if not isinstance(text, str):
        raise MorseCodeError("内容必须是文本")
    if not isinstance(morse, bool):
        raise MorseCodeError("morse 参数必须是布尔值")

    problems: List[Tuple[int, str]] = []
    if morse:
        for index, token in enumerate(text.split(), start=1):
            if token == _SLASH:
                continue
            if token not in _MORSE_TO_CHAR:
                problems.append((index, token))
        return problems

    for index, char in enumerate(text, start=1):
        if char.isspace():
            continue
        upper = char.upper()
        if len(upper) != 1 or upper not in MORSE_CODE:
            problems.append((index, char))
    return problems


def encode_text(text: str) -> str:
    """把文本编码为摩尔斯电码：字母间空格，单词间斜杠。"""
    problems = validate(text)
    if not text.strip():
        raise MorseCodeError("待编码的内容不能为空")
    if problems:
        position, char = problems[0]
        raise MorseCodeError("第 %d 个字符「%s」不支持摩尔斯编码" % (position, char))

    words: List[str] = []
    for word in text.split():
        words.append(" ".join(MORSE_CODE[char.upper()] for char in word))
    return " / ".join(words)


def decode_morse(text: str) -> str:
    """把摩尔斯电码解码为文本：空格分字母，斜杠分单词。"""
    if not isinstance(text, str):
        raise MorseCodeError("电码必须是文本")
    tokens = text.split()
    if not tokens:
        raise MorseCodeError("待解码的摩尔斯电码不能为空")

    words: List[List[str]] = [[]]
    for index, token in enumerate(tokens, start=1):
        if token == _SLASH:
            if not words[-1]:
                raise MorseCodeError(
                    "第 %d 个码元「/」位置不合法：斜杠只用于分隔单词" % index
                )
            words.append([])
            continue
        if token not in _MORSE_TO_CHAR:
            raise MorseCodeError(
                "第 %d 个码元「%s」不是合法的摩尔斯电码" % (index, token)
            )
        words[-1].append(_MORSE_TO_CHAR[token])
    if not words[-1]:
        raise MorseCodeError(
            "第 %d 个码元「/」位置不合法：斜杠只用于分隔单词" % len(tokens)
        )
    return " ".join("".join(chars) for chars in words)


def pick_words(count: int, seed: Optional[int] = None) -> Tuple[str, ...]:
    """从单词表中不重复地抽取若干练习单词。"""
    if isinstance(count, bool) or not isinstance(count, int):
        raise MorseCodeError("题目数量必须是整数")
    if not MIN_CARDS <= count <= MAX_CARDS:
        raise MorseCodeError(
            "题目数量必须在 %d~%d 之间，当前是 %d" % (MIN_CARDS, MAX_CARDS, count)
        )
    if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int)):
        raise MorseCodeError("随机种子必须是整数")

    rng = random.Random(seed)
    return tuple(rng.sample(WORDS, count))


def morse_for(word: str) -> str:
    """返回单个单词的电码，字母之间用空格分隔。"""
    if not isinstance(word, str):
        raise MorseCodeError("单词必须是文本")
    word = word.strip()
    if not word:
        raise MorseCodeError("单词不能为空")
    if any(char.isspace() for char in word):
        raise MorseCodeError("单词不能包含空格")
    problems = validate(word)
    if problems:
        position, char = problems[0]
        raise MorseCodeError("第 %d 个字符「%s」不支持摩尔斯编码" % (position, char))
    return " ".join(MORSE_CODE[char.upper()] for char in word)
