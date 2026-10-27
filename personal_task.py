import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
import time
import csv

# トップページのURL
start_url = "https://www.musashino-u.ac.jp/"
domain = urlparse(start_url).netloc

# URLとタイトルを保存する辞書
site_map = {}

# これから調べるURLのリスト
urls = [start_url]

# CSVファイルに保存する関数
def save_csv():
    with open("sitemap.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["URL", "Title"])

        for url, title in site_map.items():
            writer.writerow([url, title])

    print("CSV保存完了:", len(site_map), "件")


try:
    while urls:
        url = urls.pop(0)

        # URLの#以降を取り除く
        url = urldefrag(url).url

        # すでに取得したURLはスキップする
        if url in site_map:
            continue

        try:
            # Webページを取得する
            response = requests.get(url, timeout=15)
            response.raise_for_status()

            # HTMLページ以外はスキップする
            content_type = response.headers.get("Content-Type", "").lower()

            if "text/html" not in content_type:
                continue

            # HTMLを解析する
            soup = BeautifulSoup(response.content, "html.parser")

            # タイトルを取得する
            if soup.title:
                title = soup.title.get_text(strip=True)
            else:
                title = ""

            # URLとタイトルを辞書に保存する
            site_map[url] = title

            print("取得件数:", len(site_map), "| URL:", url, "| タイトル:", title)

            # ページ内のリンクを取得する
            for a in soup.find_all("a", href=True):
                link = urljoin(url, a["href"])

                # URLの#以降を取り除く
                link = urldefrag(link).url

                parsed = urlparse(link)

                # 同じドメインのHTTP・HTTPSリンクだけを対象にする
                if (
                    parsed.netloc == domain
                    and parsed.scheme in ("http", "https")
                    and not parsed.path.lower().endswith(
                        (
                            ".pdf", ".jpg", ".jpeg", ".png", ".gif",
                            ".zip", ".doc", ".docx", ".xls", ".xlsx",
                            ".ppt", ".pptx"
                        )
                    )
                ):
                    # 未取得かつ未登録のURLを追加する
                    if link not in site_map and link not in urls:
                        urls.append(link)

            # サーバーへの負荷を減らすため1秒待つ
            time.sleep(1)

            # 10ページ取得するごとにCSVを保存する
            if len(site_map) % 10 == 0:
                save_csv()

        except requests.exceptions.RequestException as e:
            print("ページを取得できませんでした:", url, e)

except KeyboardInterrupt:
    print("\n処理を中断しました。")

finally:
    # 終了時に、それまでの取得結果を保存する
    save_csv()

    print("取得したページ数:", len(site_map))
    print("残りのURL数:", len(urls))
    print("sitemap.csv に保存しました。")