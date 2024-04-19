import pandas as pd
from sqlalchemy import create_engine


shop_comments = pd.read_csv("./view_shop/data_shop/shop_comments.csv")
shop_details = pd.read_csv("./view_shop/data_shop/shop_details.csv")
shop_details = shop_details.drop_duplicates()

# 根据你的MySQL配置进行修改
engine = create_engine('mysql://root:123456@127.0.0.1/shop_data?charset=utf8mb4', pool_pre_ping=True)

# 假设你的DataFrame对象名为df，表名为table_name
shop_comments.to_sql(name='shop_comments', con=engine, if_exists='replace', index=False)



