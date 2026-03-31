"""
BEE Lab News & Blog 이미지 스크래퍼 v6
pip install selenium requests beautifulsoup4
python beelab_scraper_v6.py
"""
import re, time, requests
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URLS = [
    ("News", "https://www.beelab.kr/news-blog/news"),
    ("Blog", "https://www.beelab.kr/news-blog/blog"),
]
OUTPUT_DIR = Path("beelab_images")
IMG_MIN_SIZE = 5_000


def sanitize(name):
    name = re.sub(r'[\\/*?:"<>|\n\r]', '', name.strip())
    name = re.sub(r'\s+', ' ', name)
    return name[:80].rstrip() if name else "untitled"


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


def extract_bg_urls(container):
    urls = []
    for div in container.find_all(style=re.compile(r'background-image.*googleusercontent')):
        m = re.search(r'url\("?(https://[^")\s]+)"?\)', div.get('style', ''))
        if m and m.group(1) not in urls:
            urls.append(m.group(1))
    return urls


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
        urls = extract_bg_urls(w)
        if urls:
            results.append({"title": title, "images": urls})
    return results


def parse_blog(html):
    soup = BeautifulSoup(html, 'html.parser')
    skip = {"BEE's Blog", "BEE'sBlog", ""}
    results = []
    for w in soup.find_all('div', class_='LS81yb'):
        secs = w.find_all('div', class_=re.compile(r'oKdM2c'))
        pending_imgs = []
        for sec in secs:
            h2s = sec.find_all('h2')
            bg_urls = extract_bg_urls(sec)
            if bg_urls:
                pending_imgs = bg_urls
            elif h2s and pending_imgs:
                title = h2s[0].get_text(strip=True)
                if title not in skip:
                    results.append({"title": title, "images": pending_imgs})
                pending_imgs = []
    return results


def make_session(driver):
    session = requests.Session()
    session.headers.update({
        "Referer": "https://www.beelab.kr/",
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"),
    })
    for cookie in driver.get_cookies():
        session.cookies.set(cookie["name"], cookie["value"])
    return session


def download(session, url, path):
    urls_to_try = [url]
    if '=w16383' in url:
        urls_to_try.append(url.replace('=w16383', '=w1280'))
        urls_to_try.append(url.replace('=w16383', '=s0'))
    for attempt_url in urls_to_try:
        try:
            r = session.get(attempt_url, timeout=30)
            r.raise_for_status()
            if len(r.content) < IMG_MIN_SIZE:
                return False
            ct = r.headers.get("Content-Type", "")
            ext = (".png" if "png" in ct else
                   ".webp" if "webp" in ct else
                   ".gif" if "gif" in ct else ".jpg")
            path.with_suffix(ext).write_bytes(r.content)
            return True
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                time.sleep(0.5)
                continue
            print(f"  ⚠ 실패: {e}")
            return False
        except Exception as e:
            print(f"  ⚠ 실패: {e}")
            return False
    print(f"  ⚠ 403 (모든 크기 실패)")
    return False


def scrape(driver, page_type, url):
    print(f"\n{'='*60}")
    print(f"📄 {page_type}: {url}")
    print(f"{'='*60}")
    driver.get(url)
    time.sleep(5)
    print("📜 스크롤 중...")
    slow_scroll(driver)
    session = make_session(driver)

    print("🔎 게시글 분석 중...")
    if page_type == "News":
        posts = parse_news(driver.page_source)
    else:
        posts = parse_blog(driver.page_source)

    total_imgs = sum(len(p["images"]) for p in posts)
    print(f"✅ {len(posts)}개 게시글, {total_imgs}장 이미지\n")

    page_dir = OUTPUT_DIR / page_type
    total_dl = 0
    for i, post in enumerate(posts, 1):
        folder = page_dir / sanitize(post["title"])
        folder.mkdir(parents=True, exist_ok=True)
        imgs = post["images"]
        print(f"📁 [{i}/{len(posts)}] {post['title'][:55]}")
        print(f"   → {len(imgs)}장")
        for j, src in enumerate(imgs, 1):
            if download(session, src, folder / f"{j:03d}"):
                total_dl += 1
                print(f"   ✓ {j}/{len(imgs)}")
            else:
                print(f"   ✗ {j}/{len(imgs)} 스킵")
            time.sleep(0.3)
    print(f"\n📊 {page_type}: {total_dl}장 다운로드 완료")


def main():
    print("🐝 BEE Lab 이미지 스크래퍼 v6\n")
    OUTPUT_DIR.mkdir(exist_ok=True)
    driver = setup_driver()
    try:
        for pt, url in URLS:
            scrape(driver, pt, url)
    finally:
        driver.quit()
    files = sum(1 for f in OUTPUT_DIR.rglob("*") if f.is_file())
    print(f"\n{'='*60}")
    print(f"✅ 완료! 총 {files}장")
    print(f"📂 {OUTPUT_DIR.resolve()}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()