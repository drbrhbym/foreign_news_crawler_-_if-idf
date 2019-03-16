from urllib.request import urlopen
from bs4 import BeautifulSoup
import warnings, os, datetime, json
warnings.filterwarnings('ignore')




if __name__ == "__main__":

    path = "./newsfolder"
    if not os.path.exists(path):
        os.makedirs(path)

    # 開啟要爬的新聞網址檔案
    while True:
        if os.path.exists("bbc_news_url_tmp.txt"):
            # 更改檔案名字
            os.rename("bbc_news_url_tmp.txt", "bbc_news_url_tmp.txt.bak")
            with open("bbc_news_url_tmp.txt.bak", "r", encoding="utf-8") as f:
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
            news_title = news_html.find("h1", class_="story-body__h1").text
            #print(title)
        except:
            continue

        create_time = news_html.find("div", class_="date date--v2")["data-datetime"]
        #print(type(create_time))
        create_time_convert = datetime.datetime.strptime(create_time, "%d %B %Y").strftime("%Y-%m-%d")
        #print(create_time_convert)

        news_id = "bbc-" + (url.split("/")[-1])
        #print(news_id)
        news_tag = "-".join((url.split("/")[-1]).split("-")[:-1])
        # print(news_tag)

        try:
            img_link = news_html.find("img", class_="js-image-replace")["src"]
        except TypeError:
            img_link = news_html.find("span", class_="image-and-copyright-container").find("div", class_="js-delayed-image-load")["data-src"]
        except:
            continue
        #print(img_link)

        artical = news_html.find("div", class_="story-body__inner")
        content = []
        for p in artical.find_all("p"):
            content.append(p.text)
        news_content = "".join(content)
        #print(news_content)

        news_keywords = []
        for key in news_html.find_all("li", class_="tags-list__tags"):
            #print(key)
            for word in key.find("a"):
                #print(word)
                news_keywords.append(word)
        #print(key_words)

        #為了讓同一個 news_id 被覆蓋過去不要重覆存
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

        #print(content_items)
        content_all.update(content_items)

    #print(content_all)

    now = datetime.datetime.now().strftime("%Y-%m-%d")
    if not os.path.exists("./newsfolder/" + now + "_BBC_news.json"):
        with open("./newsfolder/" + now + "_BBC_news.json", "w", encoding="utf-8") as f:
            json.dump(content_all, f)

    else:
        with open("./newsfolder/" + now + "_BBC_news.json", "r", encoding="utf-8") as f:
            old_content_all = json.load(f)
            old_content_all.update(content_all)

        with open("./newsfolder/" + now + "_BBC_news.json", "w", encoding="utf-8") as f:
            json.dump(old_content_all, f)


    os.remove("bbc_news_url_tmp.txt.bak")