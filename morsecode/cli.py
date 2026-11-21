"""命令行入口：编码、解码与 A4 练习卡生成。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from .model import (
    DEFAULT_CARDS,
    MAX_CARDS,
    MIN_CARDS,
    MorseCodeError,
    decode_morse,
    encode_text,
    pick_words,
)
from .render import page_count, render_card_html

DEFAULT_CARD_FILE = "摩尔斯练习卡.html"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="morsecode",
        description="摩尔斯电码编解码：文本互转，或生成 A4 可打印练习卡",
    )
    parser.add_argument("--version", action="version", version="morsecode 0.1.0")
    parser.add_argument("--text", help="要编码的文本，例如 SOS 2026")
    parser.add_argument("--decode", help="要解码的电码，例如 ... --- ... / -.-")
    parser.add_argument("--card", action="store_true", help="生成 A4 练习卡")
    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help="练习卡题目数量（%d~%d，默认 %d）"
        % (MIN_CARDS, MAX_CARDS, DEFAULT_CARDS),
    )
    parser.add_argument("--seed", type=int, default=None, help="随机种子，便于复现")
    parser.add_argument(
        "--title", default="摩尔斯练习卡", help="练习卡标题（最多 24 个字符）"
    )
    parser.add_argument(
        "-o", "--output", default=None, help="输出文件路径；编码/解码不填则打印到屏幕"
    )
    return parser


def _write_file(path: str, content: str) -> None:
    Path(path).write_text(content, encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    mode_count = sum(
        [
            args.text is not None,
            args.decode is not None,
            bool(args.card),
        ]
    )
    if mode_count != 1:
        print(
            "错误: 请在 --text、--decode、--card 中指定且只指定一个",
            file=sys.stderr,
        )
        return 2
    if not args.card and (args.count is not None or args.seed is not None):
        print("错误: --count 与 --seed 只能和 --card 一起使用", file=sys.stderr)
        return 2

    try:
        if args.text is not None:
            result = encode_text(args.text)
            if args.output:
                _write_file(args.output, result)
                print("已写入 %s" % args.output)
            else:
                print(result)
            return 0

        if args.decode is not None:
            result = decode_morse(args.decode)
            if args.output:
                _write_file(args.output, result)
                print("已写入 %s" % args.output)
            else:
                print(result)
            return 0

        count = args.count if args.count is not None else DEFAULT_CARDS
        words = pick_words(count, seed=args.seed)
        page = render_card_html(words, title=args.title)
        target = args.output if args.output else DEFAULT_CARD_FILE
        _write_file(target, page)
        print(
            "已生成 %s：%d 道题，共 %d 页"
            % (target, len(words), page_count(len(words)))
        )
        print("用浏览器打开后按 Ctrl/Cmd + P，纸张选 A4 纵向即可打印")
        return 0
    except MorseCodeError as exc:
        print("错误: %s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("错误: 文件读写失败: %s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
