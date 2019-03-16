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
        if os.path.exists("afp_news_url_tmp.txt"):
            # 更改檔案名字
            os.rename("afp_news_url_tmp.txt", "afp_news_url_tmp.txt.bak")
            with open("afp_news_url_tmp.txt.bak", "r", encoding="utf-8") as f:
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
            news_title = news_html.find("h3", class_="htitle").text
            #print(news_title)
        except:
            logerror("afp_news_title_TypeError: " + url)
            continue

        create_time_block = news_html.find("div", class_="article_content_date")
        create_time_d = create_time_block.find("span", class_="d").text
        create_time_m = create_time_block.find("span", class_="m").text
        create_time_y = create_time_block.find("span", class_="y").text
        create_time = create_time_d + create_time_m + create_time_y
        #print(create_time)
        create_time_convert = datetime.datetime.strptime(create_time, "%d%b%Y").strftime("%Y-%m-%d")
        #print(create_time_convert)

        artical_id = (url.split("/")[-1]).split("-")[-1]
        #print(artical_id)

        news_id = "AFP-world-" + artical_id
        #print(news_id)

        news_tag = "AFP-world"

        img_link = "https://www.afp.com" + (news_html.find("div", class_="w50")).find("img")["src"]
        #print(img_link)

        artical = news_html.find("div", class_="w75")
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
    if not os.path.exists("./newsfolder/" + now + "_AFP_news.json"):
        with open("./newsfolder/" + now + "_AFP_news.json", "w", encoding="utf-8") as f:
            json.dump(content_all, f)

    else:
        with open("./newsfolder/" + now + "_AFP_news.json", "r", encoding="utf-8") as f:
            old_content_all = json.load(f)
            old_content_all.update(content_all)

        with open("./newsfolder/" + now + "_AFP_news.json", "w", encoding="utf-8") as f:
            json.dump(old_content_all, f)

    os.remove("afp_news_url_tmp.txt.bak")

    now_s = str(datetime.datetime.now())
    loginfo("afp_news_crawler_finished_" + now_s)