# 从pymongo库导入操作MongoDB相关的类
from pymongo import MongoClient


# 对操作MongoDB的方法进行封装
class Mongo:
    def __init__(self, mongo_url: str):
        # 实例化MongoClient，建立到MongoDB的连接
        self.mongo = MongoClient(mongo_url)

    # 使用db和col实例化col类
    def get_col(self, db: str, collection: str):
        # 实例化db类
        db = self.mongo[db]
        # 实例化col类
        col = db[collection]
        # 返还col对象
        return col

    # 增
    def create(self, db: str, collection: str, data: list) -> bool:
        #     try:
        #         # 获取col对象
        #         col = self.get_col(db, collection)
        #         # 操作col对象向数据库插入数据
        #         col.insert_many(data)
        #         return True
        #     except TypeError:
        #         print(data)
        # 获取col对象
        col = self.get_col(db, collection)
        # 操作col对象向数据库插入数据
        col.insert_many(data)
        return True

    # 查
    def read(self, db: str, collection: str, db_filter: dict) -> list:
        # 获取col对象
        col = self.get_col(db, collection)
        # 操作col对象从数据库读取符合要求的数据
        data = col.find(db_filter)
        # 新建空的list用于存储数据
        json_data = []
        # 遍历col对象返还的查询结果
        for item in data:
            # 建立新的dict用于存储查询结果的数据
            item_data = {}
            # 遍历返还结构中的所有键
            for key in item:
                # 舍弃掉键为"_id"的部分，该部分值为一个MongoDB ID对象，会导致结果无法转换为json
                if key == '_id':
                    # 跳过
                    pass
                    # item_data['_id'] = str(item['_id'])
                # 如果为正常数据
                else:
                    # 存入item_data
                    item_data[key] = item[key]
            # 将处理完毕的数据存入json_data
            json_data.append(item_data)
        # 返还结果
        return json_data

    # 改
    def update(self, db: str, collection: str, db_filter: dict, data: dict) -> bool:
        # 获取col对象
        col = self.get_col(db, collection)
        # 操作col对象修改数据库
        col.update_many(db_filter, {"$set": data})
        # 返还逻辑真
        return True

    # 删
    def delete(self, db: str, collection: str, db_filter: dict) -> bool:
        # 获取col对象
        col = self.get_col(db, collection)
        # 操作col对象删除数据库中符合要求的数据
        col.delete_many(db_filter)
        # 返还逻辑真
        return True

    def exist(self, db: str, collection: str, db_filter: dict):
        if len(self.read(db, collection, db_filter)) == 0:
            return False
        else:
            return True
