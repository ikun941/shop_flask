import json
import re
from collections import Counter
import jieba
import pandas as pd
from flask import Flask, request
from flask_cors import CORS
from uitl import Map_data, Kmean_map, shop_poiId
from view_shop.Database import Shop_database

# 实例化数据库对象
dp = Shop_database()

app = Flask(__name__)
CORS(app, resources=[r'/*'])


@app.route('/', methods=["GET", "POST"])
def hello_world():
    return 'Hello, World!'


@app.route('/test', methods=["GET", "POST"])
def test():
    return {"data": 'Hello, World!'}


"""
1.呈现城市餐饮店铺时空特征分布和热门店铺特色美食
"""


# 全局地图数据
@app.route('/map', methods=["GET", "POST"])
def map():
    name, longitude, latitude, poiId = Map_data()

    markers_list = []
    map_data = {}
    for n, lo, la, poiId in zip(name, longitude, latitude, poiId):
        lo = float(lo)
        la = float(la)
        position = [lo, la]

        map_data["name"] = n
        map_data["value"] = None
        map_data["poiId"] = poiId
        map_data["position"] = position
        markers_list.append(map_data.copy())

    map_json = {"data": {"markers": markers_list}}
    return map_json


@app.route('/select_shop', methods=["GET", "POST"])
def select_shop():
    # post请求接收json参数
    request_json = request.get_json()
    # 店铺名字
    shop_name = request_json["shop_name"]

    markers_list = []
    map_data = {}
    name, longitude, latitude, poiId = Map_data()
    for n, lo, la, poiId in zip(name, longitude, latitude, poiId):
        if shop_name in n:
            lo = float(lo)
            la = float(la)
            position = [lo, la]

            map_data["name"] = n
            map_data["value"] = None
            map_data["poiId"] = poiId
            map_data["position"] = position
            markers_list.append(map_data.copy())

    map_json = {"data": {"markers": markers_list}}
    return map_json


# 热门店铺——定义：均分>=4.8
@app.route("/hot_shop_map", methods=["GET", "POST"])
def hot_shop_map():
    hot_shop = dp.select_limit(table_name="shop_details", factor_str="avgScore", min_value=5, max_value=5)

    hot_shop_list = []
    hot_shop_dictt = {}
    for shop in hot_shop:
        name = shop["name"]
        longitude = shop["longitude"]
        latitude = shop["latitude"]
        poiId = shop["poiId"]

        # print(name, longitude, latitude)
        hot_shop_dictt["name"] = name
        hot_shop_dictt["poiId"] = poiId
        hot_shop_dictt["position"] = [longitude, latitude]
        hot_shop_list.append(hot_shop_dictt.copy())

    hot_shop_data = {"data": {"markers": hot_shop_list}}
    return hot_shop_data


# 品牌店铺
@app.route("/brand_shop", methods=["GET", "POST"])
def brand_shop():
    brand_shop_detail = dp.select_one_all_not(table_name="shop_details", factor_str="brandName", value=" ")
    brand_shop_list = []
    brand_shop_dictt = {}
    for shop in brand_shop_detail:
        name = shop["name"]
        longitude = shop["longitude"]
        latitude = shop["latitude"]
        poiId = shop["poiId"]

        brand_shop_dictt["name"] = name
        brand_shop_dictt["poiId"] = poiId
        brand_shop_dictt["position"] = [longitude, latitude]
        brand_shop_list.append(brand_shop_dictt.copy())

    brand_shop_data = {"data": {"markers": brand_shop_list}}
    return brand_shop_data


# 网红店铺
@app.route("/comment_shop", methods=["GET", "POST"])
def comment_shop():
    comment_shop_detail = dp.select_one_num(table_name="shop_comments", field="poiId", num=1000)
    poiId_list = []
    for comment_shops in comment_shop_detail:
        poiId = comment_shops["poiId"]
        poiId_list.append(str(poiId))

    name, longitude, latitude, poiId = shop_poiId(poiId_list)
    markers_list = []
    map_data = {}
    for n, lo, la, poiId in zip(name, longitude, latitude, poiId):
        lo = float(lo)
        la = float(la)
        position = [lo, la]

        map_data["name"] = n
        map_data["value"] = None
        map_data["poiId"] = poiId
        map_data["position"] = position
        markers_list.append(map_data.copy())

    map_json = {"data": {"markers": markers_list}}
    return map_json


"""
2.挖掘城市餐饮消费行为的地域特征倾向和时序特征，店铺消费关联关系分析
"""


# 店铺评价词云图
@app.route("/word_cloud", methods=["GET", "POST"])
def word_cloud():
    # post请求接收json参数
    request_json = request.get_json()
    # 店铺id
    poiId = request_json["poiId"]
    print("word_cloud_poiId:", poiId)
    try:
        poiId_comments = dp.select_one_all(table_name="shop_comments", factor_str="poiId", value=poiId)
        shop_details = dp.select_one_all(table_name="shop_details", factor_str="poiId", value=poiId)[0]
        print(shop_details)
        shop_name = shop_details["name"]
    except Exception as e:
        print("Exception", e)
        poiId_comments = []
        shop_name = None

    comments = []
    for comment in poiId_comments:
        c = comment["comment"]
        if c is None:
            continue
        comments.append(c)

    poiId_c = "".join(comments)
    # 去除非汉字但保留逗号和句号
    poiId_c = re.sub("[^，。\u4e00-\u9fa5]+", "", poiId_c)
    if poiId_c:
        # 使用jieba进行中文分词
        words = jieba.lcut_for_search(poiId_c)

        def remove_stopwords(words, stopwords):
            # 过滤掉指定的连接词
            return [word for word in words if word not in stopwords]

        # 指定连接词
        stopwords = ['的', '得', '一样', '还行', '一般', '可以', '因为', '味道', '没有', "来说", "还是", "就是", "这次",
                     "以前"]
        # 过滤连接词
        filtered_words = remove_stopwords(words, stopwords)

        # 统计词语出现次数
        word_counts = Counter(filtered_words)
        # 转换为指定格式的字典列表
        # 去除只包含一个字的词语
        result = [{'name': word, 'value': count} for word, count in word_counts.items() if len(word) > 1]
        # 遍历列表，移除'name'中包含"一"的字典
        for item in result:
            if '一' in item['name']:
                result.remove(item)

        return {"data": result, "shop_name": shop_name}
    else:
        return {"data": [{"name": "无评价", "value": 99}]}


# 雷达图和柱状图
@app.route("/compare_shop", methods=["GET", "POST"])
def compare_shop():
    # post请求接收json参数
    request_json = request.get_json()
    # poiId_1_2: [店铺1, 店铺2]
    poiId_1_2 = request_json["poiId_1_2"]

    if len(poiId_1_2) == 1:
        print("poiId_1_2==1:", poiId_1_2)
        shop_detail = dp.select_one_all(table_name="shop_details", factor_str="poiId", value=int(poiId_1_2[0]))[0]
        shop_name = shop_detail["name"]
        # 平均价格
        avgPrice = shop_detail["avgPrice"]
        # 平均得分
        avgScore = shop_detail["avgScore"]

        try:
            comment_detail = dp.select_one_all(table_name="shop_comments", factor_str="poiId", value=int(poiId_1_2[0]))
            sum_star = 0
            avg_star = 0
            comment_len = len(comment_detail)
            comments = 0

            for comment in comment_detail:
                sum_star += int(comment["star"])
                if comment["comment"]:
                    comments += 1

            if comment_len:
                avg_star = sum_star / comment_len

            leida = [{"value": [avgPrice, avgScore, int(avg_star), comments], "name": shop_name},
                     {"value": [0, 0, 0, 0], "name": "shop2"}]
            bar = [{"value": [avgPrice, avgScore, int(avg_star), comments], "name": shop_name},
                   {"value": [0, 0, 0, 0], "name": "shop2"}]
        except:
            leida = [{"value": [0, 0, 0, 0], "name": "shop1"},
                     {"value": [0, 0, 0, 0], "name": "shop2"}]
            bar = [{"value": [0, 0, 0, 0], "name": "shop1"},
                   {"value": [0, 0, 0, 0], "name": "shop2"}]

        return {"data": {"leida": leida, "bar": bar}}

    elif len(poiId_1_2) == 2:
        print("poiId_1_2==2:", poiId_1_2)
        shop1_detail = dp.select_one_all(table_name="shop_details", factor_str="poiId", value=int(poiId_1_2[0]))[0]
        shop_name1 = shop1_detail["name"]
        # 平均价格
        avgPrice1 = shop1_detail["avgPrice"]
        # 平均得分
        avgScore1 = shop1_detail["avgScore"]

        shop2_detail = dp.select_one_all(table_name="shop_details", factor_str="poiId", value=int(poiId_1_2[1]))[0]
        shop_name2 = shop2_detail["name"]
        # 平均价格
        avgPrice2 = shop2_detail["avgPrice"]
        # 平均得分
        avgScore2 = shop2_detail["avgScore"]

        comment_detail1 = dp.select_one_all(table_name="shop_comments", factor_str="poiId", value=int(poiId_1_2[0]))
        sum_star1 = 0
        avg_star1 = 0
        comment_len1 = len(comment_detail1)
        comments1 = 0
        for comment in comment_detail1:
            sum_star1 += int(comment["star"])
            if comment["comment"]:
                comments1 += 1
        if comment_len1:
            avg_star1 = sum_star1 / comment_len1

        comment_detail2 = dp.select_one_all(table_name="shop_comments", factor_str="poiId", value=int(poiId_1_2[1]))
        sum_star2 = 0
        avg_star2 = 0
        comment_len2 = len(comment_detail2)
        comments2 = 0
        for comment in comment_detail2:
            sum_star2 += int(comment["star"])
            if comment["comment"]:
                comments2 += 1
        if comment_len2:
            avg_star2 = sum_star2 / comment_len2

        leida = [{"value": [avgPrice1, avgScore1, int(avg_star1), comments1], "name": shop_name1},
                 {"value": [avgPrice2, avgScore2, int(avg_star2), comments2], "name": shop_name2}]

        bar = [{"value": [avgPrice1, avgScore1, int(avg_star1), comments1], "name": shop_name1},
               {"value": [avgPrice2, avgScore2, int(avg_star2), comments2], "name": shop_name2}]

        return {"data": {"leida": leida, "bar": bar}}
    else:
        leida = [{"value": [0, 0, 0, 0], "name": "shop1"},
                 {"value": [0, 0, 0, 0], "name": "shop2"}]
        bar = [{"value": [0, 0, 0, 0], "name": "shop1"},
               {"value": [0, 0, 0, 0], "name": "shop2"}]

        return {"data": {"leida": leida, "bar": bar}}


"""
3.支持针对自定义消费条件的个性化推荐
"""


@app.route('/cost_suggest', methods=["GET", "POST"])
def cost_suggest():
    # post请求接收json参数
    request_json = request.get_json()
    # 推荐条件
    shop_type = request_json["shop_type"]
    start = request_json["start"]
    end = request_json["end"]

    data_csv = pd.read_csv("data_shop/shop_details.csv", encoding="utf-8")
    # 删除与列名相同的行
    shop_details = data_csv.loc[~(data_csv == data_csv.columns).all(axis=1)]
    try:
        # 在“name”列进行模糊查询
        filtered_name = shop_details[shop_details["name"].str.contains(shop_type, case=False, na=False)]
        # 将“avgPrice”列的值转换为数字
        filtered_name['avgPrice'] = filtered_name['avgPrice'].astype(int)
        # 使用条件筛选取出在 start 和 end 之间的数据
        filtered_data = filtered_name[(filtered_name['avgPrice'] >= start) & (filtered_name['avgPrice'] <= end)]
        # avgScore排序
        filtered_data = filtered_data.sort_values(by="avgScore", ascending=False)

        name_list = []
        avgPrice_list = []
        avgScore_list = []
        avg_star_list = []
        comments_list = []
        # 前四个店铺
        if len(filtered_data) >= 4:
            names = filtered_data["name"][0:4]
            avgPrices = filtered_data["avgPrice"][0:4]
            avgScores = filtered_data["avgScore"][0:4]
        else:
            names = filtered_data["name"]
            avgPrices = filtered_data["avgPrice"]
            avgScores = filtered_data["avgScore"]

        poiIds = filtered_data["poiId"][0:4]
        for poiId, name, avgPrice, avgScore in zip(poiIds, names, avgPrices, avgScores):
            # comment_detail = dp.select_one_all(table_name="shop_comments", factor_str="poiId", value=poiId)
            # print(comment_detail)
            comment_detail_data = pd.read_csv("data_shop/shop_comments.csv", encoding="utf-8")
            comment_detail = comment_detail_data[comment_detail_data["poiId"] == int(poiId)]
            comment_detail = comment_detail.to_dict(orient='records')

            sum_star = 0
            avg_star = 0
            comment_len = len(comment_detail)
            comments = 0

            for comment in comment_detail:
                sum_star += int(comment["star"])
                if comment["comment"]:
                    comments += 1

            if comment_len:
                avg_star = sum_star / comment_len

            name_list.append(name)
            avgPrice_list.append(avgPrice)
            avgScore_list.append(avgScore)
            avg_star_list.append(int(avg_star))
            comments_list.append(comments)

        return {"data": [name_list, avgPrice_list, avgScore_list, avg_star_list, comments_list, [0, 1, 2, 3], ["avgPrice", "avgScore", "avg_star", "comments"]]}
    except Exception as e:
        print("e:", e)
        return {"data": [[None, None, None, None], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0],  [0, 1, 2, 3], ["avgPrice", "avgScore", "avg_star", "comments"]]}


"""
4.尝试构建绵阳餐饮种类大地图和消费评价大地图
"""

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
