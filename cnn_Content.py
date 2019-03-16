from urllib.request import urlopen
from bs4 import BeautifulSoup
import warnings, os, datetime, json
warnings.filterwarnings('ignore')
from log import logerror, loginfo



if __name__ == "__main__":

    path = "./newsfolder"
    if not os.path.exists(path):
        os.makedirs(path)

    # 開啟要爬的新聞網址檔案
    while True:
        if os.path.exists("cnn_news_url_tmp.txt"):
            # 更改檔案名字
            os.rename("cnn_news_url_tmp.txt", "cnn_news_url_tmp.txt.bak")
            with open("cnn_news_url_tmp.txt.bak", "r", encoding="utf-8") as f:
                url_list = f.read().split("\n")
                url_list.remove("")
            break
        else:
            time.sleep(120)

    #print(url_list)

    content_all = {}

    for url in url_list:
        url_response = urlopen(url)
        news_html = BeautifulSoup(url_response)
        #print(news_html)

        try:
            news_title = news_html.find("h1", class_="pg-headline").text
            #print(news_title)
        except:
            logerror("cnn_news_title_TypeError: " + url)
            continue

        create_time = (((news_html.find("p", class_="update-time").text).split(")")[-1]).replace(",", "")).strip(" ")
        create_time_convert = datetime.datetime.strptime(create_time, "%B %d %Y").strftime("%Y-%m-%d")
        #print(create_time_convert)

        news_id = "cnn-" + url.split("/")[7]
        #print(news_id)

        news_tag = url.split("/")[6]
        #print(news_tag)

        img_link = news_html.find("meta", itemprop="image")["content"]
        #print(img_link)

        artical = news_html.find_all("div", class_="zn-body__paragraph")
        content = []
        for p in artical:
            content.append(p.text)
            #print(p.text)
        news_content = "".join(content)
        #print(news_content)

        news_keywords = news_html.find("meta", itemprop="keywords")["content"].split(", ")
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
    if not os.path.exists("./newsfolder/" + now + "_CNN_news.json"):
        with open("./newsfolder/" + now + "_CNN_news.json", "w", encoding="utf-8") as f:
            json.dump(content_all, f)

    else:
        with open("./newsfolder/" + now + "_CNN_news.json", "r", encoding="utf-8") as f:
            old_content_all = json.load(f)
            old_content_all.update(content_all)

        with open("./newsfolder/" + now + "_CNN_news.json", "w", encoding="utf-8") as f:
            json.dump(old_content_all, f)

    os.remove("cnn_news_url_tmp.txt.bak")

    now_s = str(datetime.datetime.now())
    loginfo("cnn_news_crawler_finished_" + now_s)