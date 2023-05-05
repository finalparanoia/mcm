from dal.mongo import Mongo
from lib.lib import Libs
from uuid import uuid4
from secrets import token_hex
from dto.dto import UserDB, RegUser


class UserAuth:
    def __init__(self):
        self.db = Mongo("mongodb://localhost:27017")
        self.lib = Libs()

    def test(self):
        success = 0
        for item in ["staff", "admin"]:
            profile = {
                "username": item,
                # 姓名
                "name": item,
                # 密码
                "pwd": item,
                # 邮箱
                "email": item+"@"+item+"."+item,
                # 电话
                "phone": item,
                "level": "a"
            }
            u = RegUser.parse_obj(profile)

            if self.db.create("user", "auth", [u.dict()]):
                success += 1
        if success == 3:
            return True, "test_account generate process complete without err"
        else:
            return False, ""

    def reg(self, profile: RegUser):
        while True:
            uuid = str(uuid4())[:6]
            resp = self.db.read("user", "auth", {"username": uuid})
            if len(resp) == 0:
                break
        profile = profile.dict()
        profile["username"] = uuid
        if len(self.db.read("user", "auth", {})) == 0:
            return self.test()
        else:
            profile["level"] = "d"
        pwd = self.lib.salt_hash(token_hex(), profile["pwd"])
        profile["pwd"] = pwd
        u = UserDB.parse_obj(profile)
        if self.db.create("user", "auth", [u.dict()]):
            return True, uuid
        else:
            return False, ""

    def auth(self, uuid: str, passwd: str):
        resp = self.db.read("user", "auth", {"username": uuid})
        if len(resp) > 0:
            resp = resp[0]
            salt = resp["pwd"][0]
            if self.lib.salt_hash(salt, passwd) == resp["pwd"]:
                return True
            else:
                return False
        else:
            return False

    def update(self, profile: dict):
        username = profile["username"]
        resp = self.db.read("user", "auth", {"username": username})
        if len(resp) != 0:
            if self.db.update("user", "auth", {"username": username}, profile):
                return True
            else:
                return False
        else:
            return False

    def delete(self, username: str):
        if username != "admin":
            self.db.delete("user", "auth", {"username": username})
            return True
        else:
            return False

    def verify_admin(self, username: str):
        try:
            resp = self.db.read("user", "auth", {"username": username})
            return resp[0]["level"] == "a"
        except KeyError:
            return False
        except IndexError:
            return False

    def all(self):
        return self.db.read("user", "auth", {})
