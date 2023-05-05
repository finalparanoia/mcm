from uuid import uuid4
from dal.mongo import Mongo
from dto.dto import Project
from lib.lib import Libs


class UniBLL:
    def __init__(self):
        self.db = Mongo("mongodb://localhost:27017")
        self.db_name, self.col = "data", "profile"
        self.lib = Libs()

    # 封装的针对指定数据库的操作
    def __read__(self, db_filter: dict):
        return self.db.read(self.db_name, self.col, db_filter)

    def __create__(self, data_list: list[dict]):
        self.db.create(self.db_name, self.col, data_list)

    def __update__(self, db_filter: dict, data: dict):
        self.db.update(self.db_name, self.col, db_filter, data)

    # 创建档案
    def create(self, data: dict):
        while True:
            uuid = str(uuid4())
            resp = self.__read__({"proj_id": uuid})
            if len(resp) == 0:
                break
        p = {
            # 项目编号
            "proj_id": uuid,
            # 当前状态
            "status": "0",
            # 审计节点
            "status_seq": [{"time_stamp": self.lib.time_stamp(), "status": "create"}],
            # 申请
            "req": [data],
            # 申报审核
            "pre_audit": [],
            # 任务书
            "mis": [],
            # 初审
            "fst_audit": [],
            # 中期报告
            "mid": [],
            # 中期审核
            "mid_audit": [],
            # 结题报告
            "fin": [],
            # 结题审核
            "fin_audit": [],
        }
        self.__create__([p])
        return uuid

    # 修改档案
    def __db_update__(self, uuid: str, key: str, data: dict):
        result = self.__read__({"proj_id": uuid})[0]
        if key in result:
            result[key].append(data)
        p = Project.parse_obj(result)
        self.__update__({"proj_id": uuid}, p.dict())
        return uuid

    # 学生补充提交
    def append(self, username: str, uuid: str, key: str, data: dict, status: str):
        resp = self.get_self(username, status)
        for item in resp:
            if item["proj_id"] == uuid:
                if key in ["req", "mis", "mid", "fin"]:
                    data["time_stamp"] = self.lib.time_stamp()
                    data["status"] = status
                    data["status_seq"].append({"time_stamp": data["time_stamp"], "status": status})
                    p = Project.parse_obj(data)
                    self.__db_update__(uuid, key, p.dict())
                    return True
        return False

    # 指导老师审核
    def audit(self, username: str, uuid: str, key: str, data: dict, status: str):
        resp = self.get_self_audit(username, status)
        for item in resp:
            if item["proj_id"] == uuid:
                if key in ["pre_audit", "fst_audit", "mid_audit", "fin_audit"]:
                    data["time_stamp"] = self.lib.time_stamp()
                    data["status"] = status
                    data["status_seq"].append({"time_stamp": data["time_stamp"], "status": status})
                    p = Project.parse_obj(data)
                    self.__db_update__(uuid, key, p.dict())
                    return True
        return False

    # 通过审批
    def approve(self, username: str, uuid: str, status: str):
        resp = self.get_self_audit(username, status)
        for item in resp:
            if item["proj_id"] == uuid:
                time_stamp = self.lib.time_stamp()
                result = self.__read__({"proj_id": uuid})[0]
                result["status"] = status
                result["status_seq"].append({time_stamp, status})
                p = Project.parse_obj(result)
                self.__update__({"proj_id": uuid}, p.dict())
                return True
        return False

    # 检测项目状态
    def __test_status__(self, uuid: str, status: str):
        result = self.__read__({"proj_id": uuid})[0]
        return result["status"] == status

    # 检测用户
    def __test_member__(self, uuid: str, username: str):
        result = self.__read__({"proj_id": uuid})[0]
        return username in result["req"][0]["user"]

    # 检测老师
    def __test_teacher__(self, uuid: str, username: str):
        result = self.__read__({"proj_id": uuid})[0]
        return username in result["direct"]

    def get_all(self):
        return self.__read__({})

    def get_one(self, username, uuid: str):
        resp_audit = self.__read__({"proj_id": uuid, "req": {"$elemMatch": {"direct": username}}})
        resp = self.__read__({"proj_id": uuid, "req": {"$elemMatch": {"direct": username}}})
        result = []
        for item in resp_audit + resp:
            if item not in result:
                result.append(item)
        return result[0]

    def get_self_audit(self, username: str, status: str):
        db_filter = {"status": status, 'req': {'$elemMatch': {'user': {'$regex': username, '$options': 'i'}}}}
        return self.__read__(db_filter)

    def get_self(self, username: str, status: str):
        db_filter = {"status": status, 'req': {'$elemMatch': {'user': {'$regex': username, '$options': 'i'}}}}
        return self.__read__(db_filter)
