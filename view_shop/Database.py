from contextlib import contextmanager
import pymysql


# 数据库类
class Database:
    # **config是指连接数据库时需要的参数,这样只要参数传入正确，连哪个数据库都可以
    # 初始化时就连接数据库
    def __init__(self, config):
        # 连接数据库的参数我不希望别人可以动，所以设置私有
        self._config = config
        self.__conn = pymysql.connect(**self._config)
        self.__cursor = self.__conn.cursor()

    @contextmanager
    def auto_reconnect(self):
        try:
            # 如果连接已断开，则重新连接
            self.__conn.ping(reconnect=True)
        except:
            self.__conn = pymysql.connect(**self._config)
            self.__cursor = self.__conn.cursor()
        yield

    # 查找条件为一个的
    def select_one_all(self, table_name, value, factor_str, field="*"):
        if field == '':
            sql = f"select {field} from {table_name}"
        else:
            sql = f"select {field} from {table_name} where {factor_str} = '{value}'"
        with self.auto_reconnect():
            self.__cursor.execute(sql)
        return self.__cursor.fetchall()

    def select_one_all_not(self, table_name, value, factor_str, field="*"):
        if field == '':
            sql = f"select {field} from {table_name}"
        else:
            sql = f"select {field} from {table_name} where {factor_str} != '{value}'"
        with self.auto_reconnect():
            self.__cursor.execute(sql)
        return self.__cursor.fetchall()

    # 查找条件为一个的num条数据
    def select_one_num(self, table_name, num, field):
        sql = f"select {field}, count({field}) AS duplicate_count from {table_name} GROUP BY {field} HAVING count({field}) > {num}"
        with self.auto_reconnect():
            self.__cursor.execute(sql)
        return self.__cursor.fetchall()

    # 范围查找
    def select_limit(self, table_name, factor_str, max_value, min_value,  sort="", field="*"):
        if field == '':
            sql = f"select {field} from {table_name}"
        else:
            sql = f"select {field} from {table_name} where {factor_str}>={min_value} and {factor_str}<={max_value}"
        with self.auto_reconnect():
            self.__cursor.execute(sql)
        return self.__cursor.fetchall()

    # 范围查找并且按sort_value排序
    def select_limit_sort(self, table_name, factor_str, max_value, min_value,  sort_value="", field="*"):
        if field == '':
            sql = f"select {field} from {table_name}"
        else:
            sql = f"select {field} from {table_name} where {factor_str}>={min_value} and {factor_str}<={max_value} order by {sort_value} DESC"
        with self.auto_reconnect():
            self.__cursor.execute(sql)
        return self.__cursor.fetchall()


# 数据库相关配置
luna_config = {
    "host": '127.0.0.1',
    "port": 3306,
    "user": 'root',
    "passwd": '123456',
    "db": 'shop_data',
    "autocommit": True,
    "cursorclass": pymysql.cursors.DictCursor,
    # "client_flag":CLIENT.MULTI_STATEMENTS
}


# 实例化数据库对象
def Shop_database():
    shop_database = Database(luna_config)
    return shop_database


# dp = Shop_database()
# data = dp.select_one_all(table_name="shop_details", factor_str="avgPrice", value=50)
# data = dp.select_limit(table_name="shop_details", factor_str="avgPrice", max_value=50, min_value=0)
# print(len(data))
# print(data)
