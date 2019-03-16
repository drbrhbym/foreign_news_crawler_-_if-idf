from urllib.request import urlopen
from bs4 import BeautifulSoup
import warnings, os, datetime, json
warnings.filterwarnings('ignore')
from log import loginfo, logerror



if __name__ == "__main__":

    path = "./newsfolder"
    if not os.path.exists(path):
        os.makedirs(path)

    # 開啟要爬的新聞網址檔案
    while True:
        if os.path.exists("yomiuri_news_url_tmp.txt"):
            # 更改檔案名字
            os.rename("yomiuri_news_url_tmp.txt", "yomiuri_news_url_tmp.txt.bak")
            with open("yomiuri_news_url_tmp.txt.bak", "r", encoding="utf-8") as f:
                url_list = f.read().split("\n")
                url_list.remove("")
            break
        #else:
        #    time.sleep(120)

    #print(url_list)

    content_all = {}

    for url in url_list:
        url_response = urlopen(url)
        news_html = BeautifulSoup(url_response)
        #print(news_html)

        news_title = news_html.find("span", itemprop="headline").text
        #print(news_title)

        create_time = news_html.find("time", id="articleContentHeaderTime")["datetime"].split("T")[0]
        #print(create_time)

        news_id = "yomiuri-" + url.split("/")[-1]
        #print(news_id)

        news_tag = "World"

        try:
            img_link = news_html.find("img", id="articleContentHeaderFigureImg")["src"]
            #print(img_link)
        except Exception:
            logerror("yomiuri_news_image_KeyError: " + url)
            continue

        artical = news_html.find("div", id="articleContentBody")
        content = []
        for p in artical.find_all("p"):
            content.append(p.text)
            # print(p.text)
        news_content = "".join(content)
        #print(news_content)

        news_keywords = "None"

        # 為了讓同一個 news_id 被覆蓋過去不要重覆存
        content_items = {news_id: {
            "news_id": news_id,
            "news_link": url,
            "news_title": news_title,
            "news_create_time": create_time,
            "img_link": img_link,
            "news_content": news_content,
            "news_keyword": news_keywords,
            "news_tag": news_tag
        }}

        # print(content_items)
        content_all.update(content_items)

    #print(content_all)

    now = datetime.datetime.now().strftime("%Y-%m-%d")
    if not os.path.exists("./newsfolder/" + now + "_Yomiuri_news.json"):
        with open("./newsfolder/" + now + "_Yomiuri_news.json", "w", encoding="utf-8") as f:
            json.dump(content_all, f)

    else:
        with open("./newsfolder/" + now + "_Yomiuri_news.json", "r", encoding="utf-8") as f:
            old_content_all = json.load(f)
            old_content_all.update(content_all)

        with open("./newsfolder/" + now + "_Yomiuri_news.json", "w", encoding="utf-8") as f:
            json.dump(old_content_all, f)

    os.remove("yomiuri_news_url_tmp.txt.bak")

    now_s = str(datetime.datetime.now())
    loginfo("yomiuri_news_crawler_finished_" + now_s)





