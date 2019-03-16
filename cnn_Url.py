from urllib.request import urlopen
from bs4 import BeautifulSoup
import warnings, os
warnings.filterwarnings('ignore')


if __name__ == "__main__":


    url = "https://edition.cnn.com/world"
    url_response = urlopen(url)
    news_html = BeautifulSoup(url_response)
    #print(news_html)

    update_url_list = []
    check_list = ["_list-hierarchical-xs_article_", "Europe_list-hierarchical-xs_article_", "Middle East_list-hierarchical-xs_article_",
                  "Africa_list-hierarchical-xs_article_", "Asia _list-hierarchical-xs_article_", "CNN Business_list-hierarchical-xs_article_",
                  "Sport_list-hierarchical-xs_article_"]
    for news_class in news_html.find_all("h3", class_="cd__headline"):
        for i in check_list:
            if news_class["data-analytics"] == i:
                news_url = "https://edition.cnn.com" + news_class.find("a")["href"]
                #print(news_url)
                update_url_list.append(news_url)
    #print(update_url_list)



    old_url_list = []  # 紀錄之前爬過的新聞網址
    # 開啟紀錄全部新聞網址的檔案
    if os.path.exists("./cnn_news_url_tmp.txt"):
        with open("./cnn_news_url_tmp.txt", "r", encoding="utf-8") as f:
            old_url_list = f.read().split("\n")
            old_url_list.remove("")
        print("old_url_list:", len(old_url_list))

        url_list = []  # 紀錄更新的新聞網址
        # 不記錄重複的新聞網址
        for url in update_url_list:
            if not url in old_url_list:
                url_list.append(url)
        print("update:", len(url_list))

        if not url_list == []:
            url_list.extend(old_url_list)
            # print(url_list)

            with open("./cnn_news_url_tmp.txt", "w", encoding="utf-8") as f:
                for url in url_list:
                    f.write(str(url + "\n"))

    else:
        with open("./cnn_news_url_tmp.txt", "w", encoding="utf-8") as f:
            for url in update_url_list:
                f.write(str(url + "\n"))

