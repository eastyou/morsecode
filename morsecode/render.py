"""把练习单词渲染成 A4 纵向、每页三张的摩尔斯练习卡。"""

from __future__ import annotations

import html
from typing import List, Sequence

from .model import MAX_CARDS, MorseCodeError, morse_for, validate

CARDS_PER_PAGE = 3
MAX_TITLE = 24


def page_count(word_count: int) -> int:
    """按每页三张卡片计算页数。"""
    if isinstance(word_count, bool) or not isinstance(word_count, int):
        raise MorseCodeError("题目数量必须是整数")
    if not 1 <= word_count <= MAX_CARDS:
        raise MorseCodeError("题目数量必须在 1~%d 之间" % MAX_CARDS)
    return (word_count + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE


def _clean_words(words: Sequence[str]) -> List[str]:
    if isinstance(words, (str, bytes)):
        raise MorseCodeError("题目必须是单词序列，不能是单个字符串")
    try:
        items = list(words)
    except TypeError as exc:
        raise MorseCodeError("题目必须是单词序列") from exc
    if not items:
        raise MorseCodeError("至少需要 1 个练习单词")
    if len(items) > MAX_CARDS:
        raise MorseCodeError("练习单词最多 %d 个" % MAX_CARDS)

    cleaned: List[str] = []
    for index, word in enumerate(items, start=1):
        if not isinstance(word, str):
            raise MorseCodeError("第 %d 题必须是文本" % index)
        word = word.strip().upper()
        if not word:
            raise MorseCodeError("第 %d 题不能为空" % index)
        if any(char.isspace() for char in word):
            raise MorseCodeError("第 %d 题「%s」不能包含空格" % (index, word))
        problems = validate(word)
        if problems:
            position, char = problems[0]
            raise MorseCodeError(
                "第 %d 题「%s」第 %d 个字符「%s」不支持摩尔斯编码"
                % (index, word, position, char)
            )
        cleaned.append(word)
    return cleaned


def _card_markup(index: int, word: str) -> str:
    return (
        '<article class="card">'
        '<div class="card-top"><span class="no">%02d</span>'
        '<span class="badge">MORSE</span></div>'
        '<div class="word">%s</div>'
        '<div class="write"><span class="line"></span>'
        '<span class="line"></span></div>'
        '<p class="prompt">把单词写成摩尔斯电码，字母之间空一格</p>'
        "</article>"
        % (index, html.escape(word))
    )


def _sheet_markup(title: str, cards: List[str], page_no: int, total: int) -> str:
    return (
        '<section class="sheet">'
        '<header class="sheet-head"><span class="brand">MORSE CODE</span>'
        '<h1>%s</h1><span class="page-no">第 %d / %d 页</span></header>'
        "%s</section>"
        % (
            html.escape(title),
            page_no,
            total,
            "".join(cards),
        )
    )


def _answer_markup(title: str, words: List[str], total: int) -> str:
    rows: List[str] = []
    for index, word in enumerate(words, start=1):
        rows.append(
            '<li><span class="no">%02d</span>'
            '<span class="aw">%s</span>'
            "<code>%s</code></li>"
            % (index, html.escape(word), html.escape(morse_for(word)))
        )
    return (
        '<section class="sheet answer-sheet">'
        '<header class="answer-head"><h2>%s · 参考答案</h2>'
        '<span>共 %d 题 · 答案页</span></header>'
        '<ol class="answers">%s</ol>'
        '<p class="answer-tip">对照答案时注意：字母之间空一格，单词之间用 / 分隔。</p>'
        "</section>"
        % (html.escape(title), total, "".join(rows))
    )


def render_card_html(words: Sequence[str], title: str = "摩尔斯练习卡") -> str:
    """生成自包含的 A4 纵向练习卡页面，末尾附参考答案页。"""
    if not isinstance(title, str):
        raise MorseCodeError("标题必须是文本")
    title = title.strip()
    if not title:
        raise MorseCodeError("标题不能为空")
    if len(title) > MAX_TITLE:
        raise MorseCodeError("标题最多 %d 个字符" % MAX_TITLE)

    items = _clean_words(words)
    total_pages = page_count(len(items))
    sheets: List[str] = []
    for offset in range(0, len(items), CARDS_PER_PAGE):
        chunk = items[offset : offset + CARDS_PER_PAGE]
        cards = [
            _card_markup(offset + position + 1, word)
            for position, word in enumerate(chunk)
        ]
        sheets.append(
            _sheet_markup(title, cards, offset // CARDS_PER_PAGE + 1, total_pages)
        )
    sheets.append(_answer_markup(title, items, len(items)))

    toolbar = (
        '<div class="toolbar"><strong>%s</strong>'
        "<span>共 %d 题 · %d 张练习卡 · %d 页</span></div>"
        % (html.escape(title), len(items), len(items), total_pages)
    )
    return (
        "<!doctype html>\n"
        '<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>%s</title>\n<style>%s</style>\n</head>\n<body>\n"
        "%s\n%s\n</body>\n</html>\n"
        % (html.escape(title), _style(), toolbar, "\n".join(sheets))
    )


def _style() -> str:
    return """
  :root { color-scheme: light; }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; }
  body {
    background: #e2e8f0;
    color: #0f172a;
    padding: 7mm 0 10mm;
    font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  }
  .toolbar {
    width: 210mm;
    max-width: calc(100% - 20px);
    margin: 0 auto 5mm;
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 12px;
    color: #334155;
    font-size: 13px;
  }
  .toolbar strong { font-size: 15px; letter-spacing: 1px; }
  .toolbar span { color: #64748b; font-size: 12px; }
  .sheet {
    width: 210mm;
    max-width: 100%;
    height: 297mm;
    margin: 0 auto 7mm;
    padding: 10mm 12mm;
    background: #fff;
    box-shadow: 0 6px 22px rgba(15, 23, 42, 0.14);
    display: flex;
    flex-direction: column;
    gap: 4mm;
    overflow: hidden;
    page-break-after: always;
    break-after: page;
  }
  .sheet:last-child { page-break-after: auto; break-after: auto; }
  .sheet-head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 8px;
    padding-bottom: 2.5mm;
    border-bottom: 0.5mm solid #0f172a;
  }
  .sheet-head .brand {
    font-size: 8pt;
    letter-spacing: 1.6pt;
    color: #64748b;
  }
  .sheet-head h1 {
    margin: 0;
    font-size: 15pt;
    font-weight: 600;
    letter-spacing: 2pt;
    text-align: center;
  }
  .sheet-head .page-no { font-size: 8pt; color: #64748b; white-space: nowrap; }
  .card {
    flex: 1 1 0;
    min-height: 0;
    display: flex;
    flex-direction: column;
    padding: 4mm 6mm;
    border: 0.5mm solid #334155;
    border-radius: 2.5mm;
  }
  .card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .card-top .no {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 11mm;
    height: 11mm;
    border-radius: 50%;
    background: #0f172a;
    color: #fff;
    font-size: 12pt;
    font-weight: 600;
  }
  .card-top .badge {
    font-size: 7.5pt;
    letter-spacing: 1.5pt;
    color: #94a3b8;
  }
  .word {
    margin: 3mm 0 0;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 32pt;
    font-weight: 700;
    letter-spacing: 3pt;
    line-height: 1.15;
    word-break: break-word;
    overflow-wrap: anywhere;
  }
  .write {
    margin-top: auto;
    display: flex;
    flex-direction: column;
    gap: 10mm;
    padding: 0 0 2mm;
  }
  .write .line {
    display: block;
    height: 0;
    border-bottom: 0.35mm dashed #94a3b8;
  }
  .prompt {
    margin: 0;
    font-size: 8pt;
    color: #64748b;
    letter-spacing: 0.3pt;
  }
  .answer-sheet { gap: 3mm; }
  .answer-head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 8px;
    padding-bottom: 2.5mm;
    border-bottom: 0.5mm solid #0f172a;
  }
  .answer-head h2 {
    margin: 0;
    font-size: 15pt;
    font-weight: 600;
    letter-spacing: 1.5pt;
  }
  .answer-head span { font-size: 8pt; color: #64748b; white-space: nowrap; }
  .answers {
    list-style: none;
    margin: 0;
    padding: 0;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.6mm 8mm;
    align-content: start;
  }
  .answers li {
    display: grid;
    grid-template-columns: 9mm 27mm minmax(0, 1fr);
    align-items: baseline;
    gap: 1.5mm;
    padding: 1.6mm 0;
    border-bottom: 0.2mm dotted #cbd5e1;
    font-size: 9pt;
  }
  .answers .no { color: #94a3b8; font-size: 8pt; }
  .answers .aw {
    font-family: Georgia, "Times New Roman", serif;
    font-weight: 700;
    letter-spacing: 0.5pt;
    overflow-wrap: anywhere;
  }
  .answers code {
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
    font-size: 8.5pt;
    color: #1e293b;
    letter-spacing: 0.4pt;
    overflow-wrap: anywhere;
  }
  .answer-tip {
    margin: auto 0 0;
    font-size: 8pt;
    color: #64748b;
    border-top: 0.2mm solid #e2e8f0;
    padding-top: 2mm;
  }
  @page { size: A4 portrait; margin: 0; }
  @media screen and (max-width: 850px) {
    body { padding: 10px 0 24px; }
    .sheet {
      width: 100%;
      height: auto;
      margin: 0 0 14px;
      padding: 18px 16px;
      box-shadow: none;
      border-radius: 0;
    }
    .card { min-height: 175px; }
    .word { font-size: 26pt; }
    .answers { grid-template-columns: 1fr; }
  }
  @media print {
    body { background: #fff; padding: 0; }
    .toolbar { display: none; }
    .sheet { margin: 0; box-shadow: none; border-radius: 0; }
    .card { break-inside: avoid; page-break-inside: avoid; }
    * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }
"""
