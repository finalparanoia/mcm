from time import strftime

from hashlib import sha512


class Libs:
    @staticmethod
    def hash(data: str or bytes):
        s = sha512()
        if type(data) == str:
            data = data.encode("utf-8")
        s.update(data)
        return s.hexdigest()

    def salt_hash(self, salt: str, data: str):
        pre_hash = data+salt
        salt_hash_str = self.hash(pre_hash)
        return [salt, salt_hash_str]

    @staticmethod
    def time_stamp():
        return strftime('%Y-%m-%d')
