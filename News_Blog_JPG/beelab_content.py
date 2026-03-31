"""
BEE Lab 콘텐츠 JSON 추출기
pip install selenium beautifulsoup4
python beelab_content.py
"""
import re, time, json
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URLS = [
    ("news", "https://www.beelab.kr/news-blog/news"),
    ("blog", "https://www.beelab.kr/news-blog/blog"),
]
OUTPUT_DIR = Path("beelab_content")


def sanitize(name):
    name = re.sub(r'[\\/*?:"<>|\n\r]', '', name.strip())
    return re.sub(r'\s+', ' ', name)[:80].rstrip() or "untitled"


def setup_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,10000")
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36")
    return webdriver.Chrome(options=opts)


def slow_scroll(driver):
    total = driver.execute_script("return document.body.scrollHeight")
    pos = 0
    while pos < total:
        pos += 400
        driver.execute_script(f"window.scrollTo(0, {pos});")
        time.sleep(0.3)
        total = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)


def count_images(container):
    return len(container.find_all(
        style=re.compile(r'background-image.*googleusercontent')
    ))


def get_body_text(sections):
    parts = []
    for sec in sections:
        if sec.find_all(style=re.compile(r'background-image')):
            continue
        h_tags = sec.find_all(['h1', 'h2', 'h3'])
        if h_tags:
            raw = sec.get_text(strip=True)
            cleaned = raw.replace(h_tags[0].get_text(strip=True), '', 1).strip()
            if not cleaned:
                continue
        text = sec.get_text(separator='\n', strip=True)
        if text and len(text) > 3:
            parts.append(text)
    return '\n'.join(parts).strip()


def parse_info(body):
    info = {"date": "", "location": "", "presenters": "",
            "awards": "", "participants": ""}
    combined = ' '.join(body.split('\n'))

    m = re.search(
        r'(January|February|March|April|May|June|July|August|September|'
        r'October|November|December)\s*\n?\s*'
        r'(\d{1,2}(?:\s*[-~]\s*\d{1,2})?)\s*,?\s*(\d{4})',
        combined, re.IGNORECASE)
    if m:
        info["date"] = f"{m.group(1)} {m.group(2)}, {m.group(3)}"

    m = re.search(r'@\s*(.+?)(?:\n|$)', combined)
    if m:
        info["location"] = m.group(1).strip()

    m = re.search(r'발표자\s*[:：]\s*(.+?)(?:\n|$)', body)
    if m:
        info["presenters"] = m.group(1).strip()

    m = re.search(r'수상자\s*[:：]\s*(.+?)(?:\n|$)', body)
    if m:
        info["awards"] = m.group(1).strip()

    m = re.search(r'참여(?:자|인원)\s*[:：]\s*(.+?)(?:\n\n|\n[^\s]|$)', body, re.DOTALL)
    if m:
        info["participants"] = re.sub(r'\s+', ' ', m.group(1)).strip()

    return info


def parse_news(html):
    soup = BeautifulSoup(html, 'html.parser')
    skip = {"BEE'sNews", "BEE's News", ""}
    results = []

    for w in soup.find_all('div', class_='LS81yb'):
        h1s = w.find_all('h1')
        if not h1s:
            continue
        title = h1s[0].get_text(strip=True)
        if title in skip:
            continue

        secs = w.find_all('div', class_=re.compile(r'oKdM2c'))
        body = get_body_text(secs)
        info = parse_info(body)
        img_count = count_images(w)

        results.append({
            "title": title,
            "folder": sanitize(title),
            "image_count": img_count,
            "body": body,
            **info,
        })
    return results


def parse_blog(html):
    soup = BeautifulSoup(html, 'html.parser')
    skip = {"BEE's Blog", "BEE'sBlog", ""}
    results = []

    for w in soup.find_all('div', class_='LS81yb'):
        secs = w.find_all('div', class_=re.compile(r'oKdM2c'))
        pending_imgs = 0
        pending_body_parts = []

        for sec in secs:
            h2s = sec.find_all('h2')
            bg_count = len(sec.find_all(
                style=re.compile(r'background-image.*googleusercontent')
            ))

            if bg_count > 0:
                pending_imgs = bg_count
                pending_body_parts = []
            elif h2s and pending_imgs > 0:
                title = h2s[0].get_text(strip=True)
                if title not in skip:
                    body = get_body_text(pending_body_parts)
                    results.append({
                        "title": title,
                        "folder": sanitize(title),
                        "image_count": pending_imgs,
                        "body": body,
                    })
                pending_imgs = 0
                pending_body_parts = []
            else:
                pending_body_parts.append(sec)

    return results


def main():
    print("BEE Lab 콘텐츠 추출기\n")
    OUTPUT_DIR.mkdir(exist_ok=True)

    driver = setup_driver()
    try:
        for page_type, url in URLS:
            print(f"{'='*50}")
            print(f"{page_type}: {url}")
            driver.get(url)
            time.sleep(5)
            print("스크롤 중...")
            slow_scroll(driver)

            if page_type == "news":
                posts = parse_news(driver.page_source)
            else:
                posts = parse_blog(driver.page_source)

            out_path = OUTPUT_DIR / f"{page_type}.json"
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)

            print(f"{len(posts)}개 게시글 -> {out_path}")
            for p in posts[:5]:
                print(f"  {p['image_count']:2d}장 | {p['title'][:50]}")
            if len(posts) > 5:
                print(f"  ... 외 {len(posts)-5}개")
    finally:
        driver.quit()

    print(f"\n완료! {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()