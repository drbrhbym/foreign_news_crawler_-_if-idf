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
        if os.path.exists("dw_news_url_tmp.txt"):
            # 更改檔案名字
            os.rename("dw_news_url_tmp.txt", "dw_news_url_tmp.txt.bak")
            with open("dw_news_url_tmp.txt.bak", "r", encoding="utf-8") as f:
                url_list = f.read().split("\n")
                url_list.remove("")
            break
        #else:
        #    time.sleep(120)

    #print(url_list)

    content_all = {}

    for url in url_list:
        #print(url)
        try:
            url_response = urlopen(url)
            news_html = BeautifulSoup(url_response)
            #print(news_html)
        except Exception:
            logerror("dw_news_URL_UnicodeEncodeError: " + url)
            continue

        news_title = (news_html.find("div", class_="col3")).find("h1").text
        #print(news_title)

        create_time = (news_html.find("ul", class_="smallList").find("li").text).split("\n")[1]
        #print(create_time)
        create_time_convert = datetime.datetime.strptime(create_time, "%d.%m.%Y").strftime("%Y-%m-%d")
        #print(create_time_convert)

        news_id = "dw-" + url.split("/")[-1].split("-")[-1]
        #print(news_id)

        news_tag = "World"

        try:
            if news_html.find("img", itemprop="image")["src"].split("_")[-1] == "303.jpg":
                img_link = "https://www.dw.com" + news_html.find("img", itemprop="image")["src"]
            elif news_html.find("img", itemprop="image")["src"].split("_")[-1] == "303.jpeg":
                img_link = "https://www.dw.com" + news_html.find("img", itemprop="image")["src"]
            else:
                img_link = news_html.find("div", class_="mediaItem").find("input", {"name": "preview_image"})["value"]
        except Exception:
            logerror("dw_news_image_KeyError: " + url)
            continue

        #print(img_link)

        artical = news_html.find("div", "longText")
        content = []
        for p in artical.find_all("p"):
            content.append(p.text)
            # print(p.text)
        news_content = "".join(content)
        #print(news_content)

        news_keywords = url.split("/")[-2].split("-")
        #print(news_keywords)

        # 為了讓同一個 news_id 被覆蓋過去不要重覆存
        content_items = {news_id: {
            "news_id": news_id,
            "news_link": url,
            "news_title": news_title,
            "news_create_time": create_time_convert,
            "img_link": img_link,
            "news_content": news_content,
            "news_keyword": news_keywords,
            "news_tag": news_tag
        }}

        # print(content_items)
        content_all.update(content_items)

    #print(content_all)

    now = datetime.datetime.now().strftime("%Y-%m-%d")
    if not os.path.exists("./newsfolder/" + now + "_DW_news.json"):
        with open("./newsfolder/" + now + "_DW_news.json", "w", encoding="utf-8") as f:
            json.dump(content_all, f)

    else:
        with open("./newsfolder/" + now + "_DW_news.json", "r", encoding="utf-8") as f:
            old_content_all = json.load(f)
            old_content_all.update(content_all)

        with open("./newsfolder/" + now + "_DW_news.json", "w", encoding="utf-8") as f:
            json.dump(old_content_all, f)

    os.remove("dw_news_url_tmp.txt.bak")

    now_s = str(datetime.datetime.now())
    loginfo("dw_news_crawler_finished_" + now_s)












