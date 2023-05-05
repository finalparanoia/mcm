from uuid import uuid4
from dal.mongo import Mongo
from dto.dto import Project, TimeSeq, Request, RequestDB, Report, ReportDB, OpinionDB, Opinion, Expend, ExpendDB
from lib.lib import Libs


class V2BLL:
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

    # 时间戳
    def time_stamp(self, data: Request or Report or Opinion) -> RequestDB or ReportDB or OpinionDB or None:
        dict_data = data.dict()
        dict_data["time_stamp"] = self.lib.time_stamp()
        if type(data) == Report:
            return ReportDB.parse_obj(dict_data)
        elif type(data) == Request:
            return RequestDB.parse_obj(dict_data)
        elif type(data) == Opinion:
            return OpinionDB.parse_obj(dict_data)
        else:
            return None

    # 时间线标注
    def time_line_mark(self, p: Project, op: str) -> Project:
        tag = {"status": op, "time_stamp": self.lib.time_stamp()}
        tag = TimeSeq.parse_obj(tag)
        p.log.append(tag.dict())
        return p

    # 创建档案
    def __create_proj__(self, req: RequestDB) -> Project:
        while True:
            uuid = str(uuid4())
            resp = self.__read__({"proj_id": uuid})
            if len(resp) == 0:
                break
        p = {
            "proj_id": uuid,
            "status": "0",
            "step": "1",
            "history": [req.dict()],
            "expend": [],
            "log": [],
            "req": req.dict(),
            "fin": []
        }
        p = Project.parse_obj(p)
        p = self.time_line_mark(p, "create")
        return p

    # 补充
    def __append_proj__(self, p: Project, data: RequestDB or ReportDB) -> Project:
        if p.step == 0 or 2:
            if type(data) == RequestDB:
                p.req = data.dict()

            p.history.append(data.dict())
            # 设置为待审核状态
            p.step = 1
            p = self.time_line_mark(p, "append")
            return p

    # 通过
    def __approve_proj__(self, p: Project) -> Project:
        if p.step == 1:
            p.fin.append(p.history[-1])
            # 设置为下一阶段
            p.status += 1
            if p.status == 4:
                # 设置为结束
                p.step = 3
            else:
                # 设置为待提交
                p.step = 0
            p = self.time_line_mark(p, "approve")
            return p

    # 发回补充
    def __reject_proj__(self, p: Project, data: OpinionDB) -> Project:
        print(p.step)
        print(data.dict())
        if p.step == 1:
            p.history.append(data.dict())
            # 设置为待补充状态
            p.step = 2
            p = self.time_line_mark(p, "reject")
            return p

    def create(self, username: str, r: Request) -> str:
        r = RequestDB.parse_obj(self.time_stamp(r))
        if not r.user:
            r.user.append(username)
        elif username not in r.user:
            r.user.append(username)
        p = self.__create_proj__(r)
        if p:
            self.__create__([p.dict()])
            return p.proj_id

    # 补充
    def append(self, username: str, uuid: str, data: Request or Report):
        resp = self.get_one(username, uuid)
        print(resp)
        p = Project.parse_obj(resp)
        data = self.time_stamp(data)
        p = self.__append_proj__(p, data)
        self.__update__({"proj_id": uuid}, p.dict())

    # 通过
    def approve(self, username: str, uuid: str):
        resp = self.get_one_audit(username, uuid)
        print(resp)
        p = Project.parse_obj(resp)
        p = self.__approve_proj__(p)
        self.__update__({"proj_id": uuid}, p.dict())

    # 发回补充
    def reject(self, username: str, uuid: str, data: Opinion):
        resp = self.get_one_audit(username, uuid)
        p = Project.parse_obj(resp)
        data = self.time_stamp(data)
        p = self.__reject_proj__(p, data)
        self.__update__({"proj_id": uuid}, p.dict())

    def get_all(self):
        return self.__read__({})

    def get_one(self, username, uuid: str):
        resp = self.__read__({"proj_id": uuid, "history.user": username})
        try:
            return resp[0]
        except KeyError:
            return {}
        except IndexError:
            return {}

    def get_one_audit(self, username, uuid: str):
        print(username)
        resp = self.__read__({"proj_id": uuid, "history.direct": username})
        try:
            return resp[0]
        except KeyError:
            return {}
        except IndexError:
            return {}

    def get_self_audit(self, username: str):
        db_filter = {"history.direct": username}
        return self.__read__(db_filter)

    def get_self(self, username: str, status: int):
        db_filter = {"status": status, "history.user": username}
        return self.__read__(db_filter)

    def get_self_all(self, username: str):
        db_filter2 = {"history.user": username}
        db_filter1 = {"history.direct": username}
        resp = self.__read__(db_filter1) + self.__read__(db_filter2)
        result = []
        for item in resp:
            if item not in result:
                result.append(item)
        return result

    def expend_time_mark(self, username: str, data: Expend) -> ExpendDB:
        dict_data = data.dict()
        dict_data["time_stamp"] = self.lib.time_stamp()
        dict_data["username"] = username
        e = ExpendDB.parse_obj(dict_data)
        return e

    def __append_exp__(self, p: Project, data: ExpendDB) -> Project:
        p.expend.append(data.dict())
        p.history.append(data.dict())
        p = self.time_line_mark(p, "expend")
        return p

    def get_expend(self, username: str, uuid: str):
        resp = self.get_one(username, uuid)
        return resp["expend"]

    def create_expend(self, username: str, uuid: str, data: Expend):
        resp = self.get_one(username, uuid)
        p = Project.parse_obj(resp)
        data = self.expend_time_mark(username, data)
        p = self.__append_exp__(p, data)
        self.__update__({"proj_id": uuid}, p.dict())
