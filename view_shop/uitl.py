import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def Map_data():
    data_csv = pd.read_csv("data_shop/shop_details.csv", encoding="utf-8")
    # 删除与列名相同的行
    shop_details = data_csv.loc[~(data_csv == data_csv.columns).all(axis=1)]

    # 地名
    name = shop_details["name"]
    # 经度
    longitude = shop_details["longitude"]
    # 维度
    latitude = shop_details["latitude"]
    # poiID
    poiId = shop_details["poiId"]
    return name, longitude, latitude, poiId


def shop_poiId(poiId_list):
    data_csv = pd.read_csv("data_shop/shop_details.csv", encoding="utf-8")
    # 删除与列名相同的行
    shop_details = data_csv.loc[~(data_csv == data_csv.columns).all(axis=1)]
    shop_detail_poiId = shop_details[shop_details["poiId"].isin(poiId_list)]

    # 地名
    name = shop_detail_poiId["name"]
    # 经度
    longitude = shop_detail_poiId["longitude"]
    # 维度
    latitude = shop_detail_poiId["latitude"]
    # poiID
    poiId = shop_detail_poiId["poiId"]
    return name, longitude, latitude, poiId


# 将无标签的数据进行无监督分类——地理位置
def Kmean_map():
    data_csv = pd.read_csv("data_shop/shop_details.csv", encoding="utf-8")
    # 删除与列名相同的行
    shop_details = data_csv.loc[~(data_csv == data_csv.columns).all(axis=1)]

    # 经度
    longitude = shop_details["longitude"]
    # 维度
    latitude = shop_details["latitude"]

    cust = []
    for lo, la in zip(longitude, latitude):
        position = [float(lo), float(la)]
        cust.append(position)

    # 预估器模型
    km = KMeans(n_clusters=4)
    km.fit(cust)
    pre = km.predict(cust)
    # print("K-means分成的类别:\n", pre)
    # 用户聚类结果评估
    # 越趋近于1代表内聚度和分离度都相对较优。
    score = silhouette_score(cust, pre)
    print("K-means轮廓系数:\n", score)

    pre_data = pre.tolist()
    # print(len(pre_data))
    return pre_data

