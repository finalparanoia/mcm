from dal.mongo import Mongo
from lib.lib import Libs
from dto.dto import LogDB


class Log:
    def __init__(self):
        self.db = Mongo("mongodb://localhost:27017")
        self.lib = Libs()

    def log(self, user: str, status: str, func: str):
        log = {
            "status": status,
            # 时间
            "time_stamp": self.lib.time_stamp(),
            # 产生日志方法
            "func": func,
            # 额外元数据
            "user": user
        }
        data = LogDB.parse_obj(log)
        self.db.create("data", "log", [data.dict()])
