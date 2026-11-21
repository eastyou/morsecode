"""cli 模块单元测试：三种模式、退出码与错误输出。"""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from typing import List, Tuple

from morsecode.cli import main


class CliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_cli(self, argv: List[str]) -> Tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_encode_stdout(self) -> None:
        code, out, _ = self.run_cli(["--text", "SOS 2026"])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "... --- ... / ..--- ----- ..--- -....")

    def test_encode_lowercase(self) -> None:
        code, out, _ = self.run_cli(["--text", "sos"])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "... --- ...")

    def test_encode_to_file(self) -> None:
        target = self.root / "encoded.txt"
        code, out, _ = self.run_cli(["--text", "SOS", "-o", str(target)])
        self.assertEqual(code, 0)
        self.assertEqual(target.read_text(encoding="utf-8"), "... --- ...")
        self.assertIn("已写入", out)

    def test_decode_stdout(self) -> None:
        code, out, _ = self.run_cli(["--decode", "... --- ... / -.-"])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "SOS K")

    def test_decode_to_file(self) -> None:
        target = self.root / "decoded.txt"
        code, _, _ = self.run_cli(["--decode", "... --- ...", "-o", str(target)])
        self.assertEqual(code, 0)
        self.assertEqual(target.read_text(encoding="utf-8"), "SOS")

    def test_card_generation(self) -> None:
        target = self.root / "card.html"
        code, out, _ = self.run_cli(
            [
                "--card",
                "--count",
                "12",
                "--seed",
                "42",
                "--title",
                "摩尔斯练习卡",
                "-o",
                str(target),
            ]
        )
        self.assertEqual(code, 0)
        page = target.read_text(encoding="utf-8")
        self.assertEqual(page.count('<article class="card">'), 12)
        self.assertEqual(page.count('<section class="sheet">'), 4)
        self.assertIn("摩尔斯练习卡", page)
        self.assertIn("12 道题", out)

    def test_card_default_count(self) -> None:
        target = self.root / "card.html"
        code, _, _ = self.run_cli(["--card", "--seed", "5", "-o", str(target)])
        self.assertEqual(code, 0)
        page = target.read_text(encoding="utf-8")
        self.assertEqual(page.count('<article class="card">'), 12)

    def test_card_min_count(self) -> None:
        target = self.root / "card.html"
        code, _, _ = self.run_cli(
            ["--card", "--count", "6", "--seed", "1", "-o", str(target)]
        )
        self.assertEqual(code, 0)
        page = target.read_text(encoding="utf-8")
        self.assertEqual(page.count('<article class="card">'), 6)
        self.assertEqual(page.count('<section class="sheet">'), 2)

    def test_card_max_count(self) -> None:
        target = self.root / "card.html"
        code, _, _ = self.run_cli(
            ["--card", "--count", "30", "--seed", "1", "-o", str(target)]
        )
        self.assertEqual(code, 0)
        page = target.read_text(encoding="utf-8")
        self.assertEqual(page.count('<article class="card">'), 30)
        self.assertEqual(page.count('<section class="sheet">'), 10)

    def test_card_seed_reproducible(self) -> None:
        first = self.root / "a.html"
        second = self.root / "b.html"
        for target in (first, second):
            code, _, _ = self.run_cli(
                ["--card", "--count", "9", "--seed", "2026", "-o", str(target)]
            )
            self.assertEqual(code, 0)
        self.assertEqual(first.read_text(encoding="utf-8"), second.read_text(encoding="utf-8"))

    def test_card_seed_changes_words(self) -> None:
        first = self.root / "a.html"
        second = self.root / "b.html"
        self.run_cli(["--card", "--count", "9", "--seed", "1", "-o", str(first)])
        self.run_cli(["--card", "--count", "9", "--seed", "2", "-o", str(second)])
        self.assertNotEqual(
            first.read_text(encoding="utf-8"), second.read_text(encoding="utf-8")
        )

    def test_count_out_of_range(self) -> None:
        for count in ("5", "31", "0"):
            with self.subTest(count=count):
                target = self.root / ("card-%s.html" % count)
                code, _, err = self.run_cli(
                    ["--card", "--count", count, "-o", str(target)]
                )
                self.assertEqual(code, 2)
                self.assertIn("6~30", err)
                self.assertFalse(target.exists())

    def test_non_integer_count(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stderr(io.StringIO()):
                main(["--card", "--count", "abc"])
        self.assertEqual(ctx.exception.code, 2)

    def test_count_without_card(self) -> None:
        code, _, err = self.run_cli(["--text", "SOS", "--count", "10"])
        self.assertEqual(code, 2)
        self.assertIn("--card", err)

    def test_seed_without_card(self) -> None:
        code, _, err = self.run_cli(["--decode", "...", "--seed", "1"])
        self.assertEqual(code, 2)
        self.assertIn("--card", err)

    def test_no_mode(self) -> None:
        code, _, err = self.run_cli([])
        self.assertEqual(code, 2)
        self.assertIn("--text", err)

    def test_text_and_decode_conflict(self) -> None:
        code, _, err = self.run_cli(["--text", "SOS", "--decode", "..."])
        self.assertEqual(code, 2)
        self.assertIn("只指定一个", err)

    def test_card_and_text_conflict(self) -> None:
        code, _, _ = self.run_cli(["--card", "--text", "SOS"])
        self.assertEqual(code, 2)

    def test_card_and_decode_conflict(self) -> None:
        code, _, _ = self.run_cli(["--card", "--decode", "..."])
        self.assertEqual(code, 2)

    def test_invalid_text(self) -> None:
        target = self.root / "out.txt"
        code, _, err = self.run_cli(["--text", "SOS中", "-o", str(target)])
        self.assertEqual(code, 2)
        self.assertIn("中", err)
        self.assertFalse(target.exists())

    def test_invalid_decode(self) -> None:
        code, _, err = self.run_cli(["--decode", "... xyz"])
        self.assertEqual(code, 2)
        self.assertIn("xyz", err)

    def test_empty_text(self) -> None:
        code, _, err = self.run_cli(["--text", ""])
        self.assertEqual(code, 2)
        self.assertIn("不能为空", err)

    def test_write_error(self) -> None:
        target = self.root / "missing" / "out.html"
        code, _, err = self.run_cli(["--text", "SOS", "-o", str(target)])
        self.assertEqual(code, 1)
        self.assertIn("文件读写失败", err)

    def test_card_write_error(self) -> None:
        target = self.root / "missing" / "card.html"
        code, _, err = self.run_cli(
            ["--card", "--count", "6", "--seed", "1", "-o", str(target)]
        )
        self.assertEqual(code, 1)
        self.assertIn("文件读写失败", err)

    def test_help(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stdout(io.StringIO()):
                main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_version(self) -> None:
        out = io.StringIO()
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stdout(out):
                main(["--version"])
        self.assertEqual(ctx.exception.code, 0)
        self.assertIn("morsecode 0.1.0", out.getvalue())


if __name__ == "__main__":
    unittest.main()
