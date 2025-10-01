# -*- coding: utf-8 -*-
"""
README의 <!-- BLOG-POST-LIST:START --> ... <!-- BLOG-POST-LIST:END --> 구간을
RSS 최신 글 목록으로 교체한다.

실행 예:
  python scripts/update_readme.py "https://yoonbitnara.github.io/feed.xml" 5 "yyyy-mm-dd"

출력 포맷(클릭 이동):
  [[yyyy-mm-dd] 제목](링크)
  - 화면엔 [yyyy-mm-dd] 제목 으로 보이고, 줄 전체 클릭 시 해당 글로 이동

주의:
  - README에 마커(START/END)가 반드시 존재해야 함
  - feedparser가 제공하는 published/updated 날짜가 없으면 [----]로 표시
"""

import sys
import os
import re
import feedparser
from datetime import datetime

START_MARKER = "<!-- BLOG-POST-LIST:START -->"
END_MARKER = "<!-- BLOG-POST-LIST:END -->"

def parse_args():
    rss_url = sys.argv[1] if len(sys.argv) > 1 else ""
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    date_format = sys.argv[3] if len(sys.argv) > 3 else "yyyy-mm-dd"
    if not rss_url:
        print("RSS URL이 필요합니다. 예) python scripts/update_readme.py https://yoonbitnara.github.io/feed.xml 5 yyyy-mm-dd")
        sys.exit(1)
    if count < 1:
        count = 5
    return rss_url, count, date_format

def fmt_date(entry, date_format):
    """
    feedparser entry에서 날짜 추출 → 문자열 포맷으로 반환.
    우선순위: published_parsed → updated_parsed
    """
    tm = None
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        tm = entry.published_parsed
    elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
        tm = entry.updated_parsed
    if not tm:
        return ""
    dt = datetime(*tm[:6])
    if date_format == "yyyy.mm.dd":
        return dt.strftime("%Y.%m.%d")
    # 기본
    return dt.strftime("%Y-%m-%d")

def build_block(entries, count, date_format):
    """
    원하는 출력: [[yyyy-mm-dd] 제목](링크)
    링크가 없으면 [yyyy-mm-dd] 제목 (비링크)로 처리
    """
    lines = []
    for ent in entries[:count]:
        title = getattr(ent, "title", "(제목 없음)") or "(제목 없음)"
        title = " ".join(title.splitlines()).strip()

        link = getattr(ent, "link", "") or getattr(ent, "id", "") or ""
        date_str = fmt_date(ent, date_format) or "----"

        if link:
            # 줄 전체가 클릭되게 앵커로 감쌈
            line = f"[[{date_str}] {title}]({link})"
        else:
            line = f"[{date_str}] {title}"

        lines.append(line)

    if not lines:
        lines.append("[----] 최근 글을 찾지 못했습니다.")
    return "\n".join(lines)

def replace_between_markers(text, new_block):
    """
    README 내 START~END 사이 블록을 new_block으로 교체
    """
    pattern = re.compile(re.escape(START_MARKER) + r"[\s\S]*?" + re.escape(END_MARKER), re.M)
    if not pattern.search(text):
        print("README에 마커가 없습니다. START/END 주석을 확인하세요.")
        sys.exit(1)
    replacement = START_MARKER + "\n" + new_block + "\n" + END_MARKER
    return pattern.sub(replacement, text)

