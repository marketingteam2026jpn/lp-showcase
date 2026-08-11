#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
leango.co.jp/dejam/function/lp/ のHTMLをそのまま流用し
  1. FVを差し替え
  2. FV直下に課題セクションを挿入
  3. 相対パスの資産を絶対URL / ローカルへ張り替え
した index.html を GitHub Pages 用に出力する。
"""
import re, sys, pathlib

HERE = pathlib.Path(__file__).parent
OUT_DIR = pathlib.Path("/tmp/lp-showcase/dejam-lp-official-fv")

src = (HERE / "original_lp.html").read_text(encoding="utf-8")
fv_new = (HERE / "fv_new.html").read_text(encoding="utf-8")
issue_new = (HERE / "issue_new.html").read_text(encoding="utf-8")
inject_css = (HERE / "inject.css").read_text(encoding="utf-8")

# ---- 1. FV差し替え -------------------------------------------------------
FV_START = '<section id="first-view"'
FV_END = '</div> <section class="lp-feature'
i = src.index(FV_START)
j = src.index(FV_END)
src = src[:i] + fv_new + "\n" + src[j:]

# ---- 2. 課題セクション挿入（F5F6F1の帯を閉じた直後＝白背景側）-------------
anchor = '</div> <section class="lp-feature'
k = src.index(anchor)
src = src[:k] + "</div>\n" + issue_new + '\n<section class="lp-feature' + src[k + len(anchor):]

# ---- 3. 資産パスの張り替え ------------------------------------------------
# CSSはローカル（フォントがCORS未許可のため本体からは読めない）
src = src.replace('href="/_astro/_division_.CPspHmBx.css"', 'href="./assets/division.css"')
# 画像・動画・favicon・内部リンクは本番サイトへ絶対URL化
def abs_url(m):
    attr, path = m.group(1), m.group(2)
    if path.startswith("//"):
        return m.group(0)
    return f'{attr}="https://leango.co.jp{path}"'

src = re.sub(r'\b(src|href)="(/[^"]*)"', abs_url, src)
# 自前で置いたローカル参照が巻き込まれていたら戻す
src = src.replace('https://leango.co.jp./assets/', './assets/')

# ---- 4. head へ追記 -------------------------------------------------------
head_add = (
    '<meta name="robots" content="noindex, nofollow">\n'
    "<style>\n" + inject_css + "\n</style>\n"
)
# 既存の robots は打ち消す（検証用ページなのでインデックスさせない）
src = src.replace('<meta name="robots" content="index, follow">', "")
src = src.replace("</head>", head_add + "</head>", 1)

OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / "index.html").write_text(src, encoding="utf-8")
print("written:", OUT_DIR / "index.html", len(src), "bytes")

# ---- 検証 ---------------------------------------------------------------
leftovers = set(re.findall(r'\b(?:src|href)="(/[^"]*)"', src))
print("root-relative leftovers:", leftovers or "none")
for must in ["使いにくいLPツール", "記事LP運用で、こんな悩みはないですか？", "それが、", "Dejamの記事LP制作機能の特徴", "./assets/division.css"]:
    print(("OK  " if must in src else "NG  ") + must)
print("first-view count:", src.count('id="first-view"'))
print("lp_pr.mp4 count:", src.count("lp_pr.mp4"))
