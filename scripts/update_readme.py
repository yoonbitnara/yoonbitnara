# -*- coding: utf-8 -*-
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
    return dt.strftime("%Y-%m-%d")

def build_block(entries, count, date_format):
    lines = []
    for ent in entries[:count]:
        title = getattr(ent, "title", "(제목 없음)") or "(제목 없음)"
        title = " ".join(title.splitlines()).strip()
        link = getattr(ent, "link", "") or getattr(ent, "id", "") or ""
        date_str = fmt_date(ent, date_format) or "----"
        if link:
            line = f"[[{date_str}] {title}]({link})"
        else:
            line = f"[{date_str}] {title}"
        lines.append(line)
    if not lines:
        lines.append("[----] 최근 글을 찾지 못했습니다.")
    return "\n".join(lines)

def replace_between_markers(text, new_block):
    pattern = re.compile(re.escape(START_MARKER) + r"[\s\S]*?" + re.escape(END_MARKER), re.M)
    if not pattern.search(text):
        print("README에 마커가 없습니다. START/END 주석을 확인하세요.")
        print("찾는 START_MARKER:", START_MARKER)
        print("찾는 END_MARKER  :", END_MARKER)
        sys.exit(1)
    replacement = START_MARKER + "\n" + new_block + "\n" + END_MARKER
    return pattern.sub(replacement, text)

def main():
    rss_url, count, date_format = parse_args()
    print(f"[INFO] 피드 가져오는 중: {rss_url}")
    feed = feedparser.parse(rss_url)

    if feed.bozo:
        print(f"[WARN] 피드 파싱 경고(bozo): {feed.bozo_exception}")

    entries = feed.entries if hasattr(feed, "entries") else []
    print(f"[INFO] 피드 항목 수: {len(entries)}")

    new_block = build_block(entries, count, date_format)
    print("[DEBUG] 생성된 블록(아래):")
    print("-----8<-----")
    print(new_block)
    print("----->8-----")

    readme_path = os.path.join(os.getcwd(), "README.md")
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 마커 존재 여부/위치 힌트
    start_idx = content.find(START_MARKER)
    end_idx = content.find(END_MARKER)
    print(f"[DEBUG] README 내 START idx: {start_idx}, END idx: {end_idx}")

    updated = replace_between_markers(content, new_block)

    if updated != content:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(updated)
        print(f"[INFO] README 갱신 완료 ({min(len(entries), count)}개 항목).")
    else:
        print("[INFO] 변경 사항 없음.")

if __name__ == "__main__":
    main()
