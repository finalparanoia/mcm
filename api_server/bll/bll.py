from uuid import uuid4
from dal.mongo import Mongo
from lib.lib import Libs
from dto.dto import Item, Task, Transport, ItemDB, TaskDB, TransportDB


class BLL:
    def __init__(self):
        self.db = Mongo("mongodb://localhost:27017")
        self.db_name, self.col = "data", "profile"
        self.lib = Libs()

    def create_item(self, i: Item):
        while True:
            uuid = str(uuid4())[:6]
            resp = self.db.read("data", "item", {"uuid": uuid})
            if len(resp) == 0:
                break
        data = i.dict()
        data["uuid"] = uuid
        data = ItemDB.parse_obj(data)
        self.db.create("data", "item", [data.dict()])

    def read_item(self, uuid: str):
        return self.db.read("data", "item", {"uuid": uuid})

    def query_item(self, name: str):
        return self.db.read("data", "item", {"name": {"$regex": name, "$options": "$i"}})

    def update_item(self, uuid: str, n: int):
        if n >= 0:
            data = self.read_item(uuid)
            if data:
                data = data[0]
                data["num"] = n
                self.db.update("data", "item", {"uuid": uuid}, data)
                return True
            else:
                return False
        else:
            return False

    def create_task(self, t: Task):
        while True:
            uuid = str(uuid4())[:6]
            resp = self.db.read("data", "task", {"uuid": uuid})
            if len(resp) == 0:
                break
        data = t.dict()
        data["uuid"] = uuid
        data["status"] = "wait"
        data = TaskDB.parse_obj(data)
        self.db.create("data", "task", [data.dict()])
        return uuid

    def read_task(self, uuid: str):
        return self.db.read("data", "task", {"uuid": uuid})

    def all_task(self):
        return self.db.read("data", "task", {})

    def update_task(self, uuid: str, status: str):
        data = self.db.read("data", "task", {"uuid": uuid})
        if status in ["wait", "processing", "finish"] and data:
            data = data[0]
            data["status"] = status
            self.db.update("data", "task", {"uuid": uuid}, data)

    def create_transport(self, t: Transport, username):
        data = t.dict()
        data["uuid"] = username
        data["start_time"] = self.lib.time_stamp()
        data["status"] = "processing"
        data = TransportDB.parse_obj(data)
        self.db.create("data", "transport", [data.dict()])

    # def read_transport(self):
    #     pass

    def update_transport(self, t_id: str, status: str):
        data = self.db.read("data", "transport", {"t_id": t_id})
        if data and status in ["proceed", "finish"]:
            data = data[0]
            data["status"] = status
            self.db.update("data", "transport", {"t_id": t_id}, data)
            return True
        else:
            return False

    def all_transport(self):
        return self.db.read("data", "transport", {})
