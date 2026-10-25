
import requests
import time
import csv
from collections import deque
from urllib.parse import urljoin, urlparse, urldefrag
from bs4 import BeautifulSoup

# 巡回を開始するURL
start_url = "https://www.musashino-u.ac.jp/"

# 同じドメインかどうかを判定するためのURL
domain = "www.musashino-u.ac.jp"

# URLをキー、タイトルを値にする辞書
site_map = {}

# これから調べるURLを保存するキュー
url_queue = deque([start_url])

# すでに調べたURLを保存する集合
visited = set()

# CSVファイルに保存する処理
def save_csv():
    with open("sitemap.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["URL", "Title"])

        for url, title in site_map.items():
            writer.writerow([url, title])


try:
    # キューにURLがある間、繰り返す
    while url_queue:
        url = url_queue.popleft()

        # すでに調べたURLは飛ばす
        if url in visited:
            continue

        visited.add(url)

        try:
            # サーバーへの負荷を減らすために待つ
            time.sleep(1.5)

            # Webページを取得する
            response = requests.get(url, timeout=20)
            response.raise_for_status()

            # HTMLページ以外は飛ばす
            if "text/html" not in response.headers.get("Content-Type", "").lower():
                continue

            # HTMLを解析する
            soup = BeautifulSoup(response.content, "html.parser")

            # titleタグの文字列を取得する
            title_tag = soup.find("title")
            title = title_tag.get_text(strip=True) if title_tag else ""

            # URLとタイトルを辞書に格納する
            site_map[url] = title

            print(f"取得ページ数: {len(site_map)}")
            print(f"取得: {url} {title}")

            # 取得した結果をCSVに保存する
            save_csv()

            # ページ内のリンクをすべて調べる
            for a in soup.find_all("a", href=True):
                next_url = urljoin(response.url, a["href"])

                # #sectionなどのページ内リンクを取り除く
                next_url, _ = urldefrag(next_url)

                # 同じドメインのURLだけをキューに追加する
                parsed_url = urlparse(next_url)

                if (
                    parsed_url.scheme in ("http", "https")
                    and parsed_url.hostname == domain
                    and next_url not in visited
                    and next_url not in url_queue
                ):
                    url_queue.append(next_url)

        except requests.RequestException as error:
            print(f"取得エラー: {url} {error}")

except KeyboardInterrupt:
    print("\n巡回を中断しました。")

finally:
    # 最後にもう一度CSVに保存する
    save_csv()

    print("巡回したページ数:", len(site_map))
    print("CSVファイル: sitemap.csv")
# サイトマップの取得結果をCSVファイルに保存
