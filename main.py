import json, datetime, shutil, time
from log import loginfo, logerror

########## Combine all the news ############

now = datetime.datetime.now().strftime("%Y-%m-%d")
# print(now)

try:
    with open("/home/cb104_g4user/afp_news/newsfolder/" + now + "_AFP_news.json") as f:
        data1 = json.load(f)
        # print(data1)
    with open("/home/cb104_g4user/bbc_news/newsfolder/" + now + "_BBC_news.json") as f:
        data2 = json.load(f)
        # print(data2)
        data1.update(data2)
    with open("/home/cb104_g4user/cnn_news/newsfolder/" + now + "_CNN_news.json") as f:
        data3 = json.load(f)
        # print(data3)
        data1.update(data3)
    with open("/home/cb104_g4user/dw_news/newsfolder/" + now + "_DW_news.json") as f:
        data4 = json.load(f)
        # print(data4)
        data1.update(data4)
    with open("/home/cb104_g4user/reuters_news/newsfolder/" + now + "_Reuters_news.json") as f:
        data5 = json.load(f)
        # print(data5)
        data1.update(data5)
    with open("/home/cb104_g4user/yomiuri_news/newsfolder/" + now + "_Yomiuri_news.json") as f:
        data6 = json.load(f)
        # print(data6)
        data1.update(data6)
    # print(data1)
except Exception:
    time.sleep(3600)


with open('all_data.json', 'w') as outfile:
    json.dump(data1, outfile)

############## ETL the special symbols of all news' content ##################

import re

characters = '[’!"#$%&\()*+,./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~üö]+'

raw_documents = []

for i in data1:
    content_sub = str(re.sub(characters, "", data1[i]["news_content"]).lower())
    raw_documents.append(content_sub)
# print(raw_documents)

############## Start tf-idfing by using Gensim ################

from gensim import corpora, models
import jieba

texts = [[word for word in jieba.cut(document, cut_all=True)] for document in raw_documents]
# print(texts)

dictionary = corpora.Dictionary(texts)
# print(dictionary)
# print(dictionary.token2id)

corpus = [dictionary.doc2bow(text) for text in texts]
# print(corpus)

tfidf = models.TfidfModel(corpus)
# print(tfidf)

corpus_tfidf = tfidf[corpus]
# print(corpus_tfidf)

all_score_list = []
for item in corpus_tfidf:
    # print(item)
    score = sorted(item, key=lambda a: a[1], reverse=True)[:8]
    # print(score)
    each_score_list = []
    for i in score:
        # print(i)
        each_score_list.append(i[0])
    # print(each_score_list)
    all_score_list.append(each_score_list)
# print(all_score_list)

############## Combine news id and scores ################

all_id_list = []
for i in data1:
    id_ = data1[i]["news_id"]
    # print(id_)
    all_id_list.append(id_)
# print(all_id_list)

cal_combine = dict(zip(all_id_list, all_score_list))
# print(cal_combine)

############## Spark word count ################

combine_score_list = []
for i in all_score_list:
    combine_score_list.extend(i)
# print(combine_score_list)

str_scores = ' '.join(str(e) for e in combine_score_list)
# print(str_scores)

with open("scores_Output.txt", "w") as text_file:
    text_file.write(str_scores)

import findspark

findspark.init()
from pyspark import SparkConf
from pyspark import SparkContext

sc = SparkContext.getOrCreate()

shutil.rmtree('count_Output.txt')

lines = sc.textFile("file:///home/cb104_g4user/demo_code/scores_Output.txt")
# print(lines)
words = lines.flatMap(lambda x: x.split(" "))
# print(words)
word_counts = words.map(lambda x: (x, 1)).reduceByKey(lambda x, y: (x + y))
# print(word_counts)
word_counts.saveAsTextFile("file:///home/cb104_g4user/demo_code/count_Output.txt")

############## Searching for the most-used keywords ################

with open("count_Output.txt/part-00000", "r") as f:
    data_000 = f.read()

data_000 = data_000.replace(")", "").replace("(", "").replace("'", "").strip(" ").split("\n")
# print(data_000)

with open("count_Output.txt/part-00001", "r") as f:
    data_001 = f.read()

data_001 = data_001.replace(")", "").replace("(", "").replace("'", "").strip(" ").split("\n")
# print(data_001)

data_000.extend(data_001)
# print(data_000)

new_list = []
for i in data_000:
    new_list.append(i.split(", "))

new_list = [x for x in new_list if x != ['']]
# print(new_list)

final_key_list = []
for i in new_list:
    if int(i[1]) >= 10:
        # print(type(i))
        final_key_list.append(i[0])
# print(final_key_list)

final_news_id_list = []
for i in cal_combine:
    # print(cal_combine[i])
    for n in cal_combine[i]:
        if str(n) in final_key_list:
            # print(i)
            final_news_id_list.append(i)
            break
# print(final_news_id_list)

############## Uploade to SQL server ################

import pymysql

databaseServer = "35.222.24.169"
databaseUser = "root"
databaseUserPwd = "root"
databaseName = "news"
databaseCharSet = "utf8mb4"
dbConnection = pymysql.connect(host=databaseServer,
                               user=databaseUser,
                               password=databaseUserPwd,
                               db=databaseName,
                               charset=databaseCharSet,
                               autocommit=True)

import findspark

findspark.init()
from pyspark.sql import SparkSession

spark = SparkSession \
    .builder \
    .appName("foreign_news") \
    .getOrCreate()

from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://{}:{}@{}/{}?charset={}".format('root', 'root', '35.222.24.169:3306', 'news', 'utf8mb4'))
con = engine.connect()  # 创建连接

data_df = spark.read.json("file:///home/cb104_g4user/demo_code/all_data.json")
# data_df.show()

try:
    cursorInstance = dbConnection.cursor()
    sqlDropTable = "DROP TABLE IF EXISTS {}".format("hot_foreign_news")
    cursorInstance.execute(sqlDropTable)
except Exception as ex:
    print("Exception occured: %s" % ex)

try:
    cursorInstance = dbConnection.cursor()
    sqlDropTable = "DROP TABLE IF EXISTS {}".format("hot_foreign_news_id")
    cursorInstance.execute(sqlDropTable)
except Exception as ex:
    print("Exception occured: %s" % ex)

for i in data_df:
    app = data_df.select(i.news_id.alias('news_id'), i.news_link.alias('news_link'), i.img_link.alias('img_link'),
                         i.news_title.alias('news_title'));
    app.registerTempTable("app");
    app_pd = app.toPandas()
    # app_pd
    app_pd.to_sql(name='hot_foreign_news', con=con, if_exists='append', index=False)
    # app.show()

from pyspark.sql.types import *

final_news_id_df = spark.createDataFrame(final_news_id_list, StringType())

for i in final_news_id_df:
    put = final_news_id_df.select(i.alias('news_id'));
    put.registerTempTable("put");
    put_pd = put.toPandas()
    # app_pd
    put_pd.to_sql(name='hot_foreign_news_id', con=con, if_exists='append', index=False)
    # app.show()

try:
    cursorInstance = dbConnection.cursor()
    sqlDeleteRows = "DELETE FROM hot_foreign_news WHERE news_id NOT IN (SELECT news_id FROM hot_foreign_news_id)"
    cursorInstance.execute(sqlDeleteRows)
except Exception as ex:
    print("Exception occured: %s" % ex)
finally:
    dbConnection.close()

now_s = str(datetime.datetime.now())
loginfo("hot_foreign_news_updated_" + now_s)



