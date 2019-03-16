from urllib.request import urlopen
from bs4 import BeautifulSoup
import warnings, os
warnings.filterwarnings('ignore')


if __name__ == "__main__":


    url = "https://www.bbc.com/news"
    url_response = urlopen(url)
    news_html = BeautifulSoup(url_response)

    update_url_list = []
    for news_block in news_html.find("ol", class_="gel-layout__item"):
        #print(news_block)
        for page_url_partial in news_block.find_all("a", class_="gs-c-promo-heading"):
            page_url = "https://www.bbc.com" + page_url_partial["href"]
            #print(page_url)
            update_url_list.append(page_url)

    #print(url_list)

    old_url_list = []  # 紀錄之前爬過的新聞網址
    # 開啟紀錄全部新聞網址的檔案
    if os.path.exists("./bbc_news_url_tmp.txt"):
        with open("./bbc_news_url_tmp.txt", "r", encoding="utf-8") as f:
            old_url_list = f.read().split("\n")
            old_url_list.remove("")
        #print("old_url_list:", len(old_url_list))

        url_list = []  # 紀錄更新的新聞網址
            # 不記錄重複的新聞網址
        for url in update_url_list:
            if not url in old_url_list:
                url_list.append(url)
        #print("update:", len(url_list))

        if not url_list == []:
            url_list.extend(old_url_list)
            #print(url_list)

            with open("./bbc_news_url_tmp.txt", "w", encoding="utf-8") as f:
                for url in url_list:
                    f.write(str(url + "\n"))

    else:
        with open("./bbc_news_url_tmp.txt", "w", encoding="utf-8") as f:
            for url in update_url_list:
                f.write(str(url + "\n"))
