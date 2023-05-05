from pydantic import BaseModel


# 登录
class Login(BaseModel):
    username: str
    password: str


# 用户
class RegUser(BaseModel):
    # 站点
    site: str
    # 姓名
    name: str
    # 密码
    pwd: str
    # 邮箱
    email: str
    # 电话
    phone: str


class UserDB(BaseModel):
    # 站点
    site: str
    # 人员唯一标识
    uuid: str
    # 密码hash盐
    salt: str
    # 密码加盐hash
    pwd: str
    # 权限
    pms: str
    # 姓名
    name: str
    # 邮箱
    email: str
    # 电话
    phone: str
    # 权限级别
    level: str


# 请求货物
class Item(BaseModel):
    # 名称
    name: str
    # 舱内货物数量
    num: int
    # 舱内寻路
    loc: dict
    # 扩展元数据
    meta_data: dict


# 仓内货物
class ItemDB(BaseModel):
    # 名称
    name: str
    # 货物唯一标识
    uuid: str
    # 舱内货物数量
    num: int
    # 舱内寻路
    loc: dict
    # 扩展元数据
    meta_data: dict


# 转运请求
class Task(BaseModel):
    # 站点ID
    site: str
    # 请求生成的时间戳
    time_stamp: str
    # 请求数量
    num: int
    # 请求物品id
    i_id: str


# 转运请求
class TaskDB(BaseModel):
    # 请求的唯一ID
    uuid: str
    # 站点ID
    site: str
    # 请求生成的时间戳
    time_stamp: str
    # 状态
    status: str
    # 请求数量
    num: int
    # 请求物品id
    i_id: str


# 转运过程
class Transport(BaseModel):
    # 预计到达时间
    init_eta: str
    # 转运请求id
    t_id: str


# 转运过程
class TransportDB(BaseModel):
    # 转运单位id
    uuid: str
    # 转运开始时间
    start_time: str
    # 预计到达时间
    init_eta: str
    # 转运请求id
    t_id: str
    # 状态
    status: str


# 日志
class LogDB(BaseModel):
    # 等级
    status: str
    # 时间
    time_stamp: str
    # 产生日志方法
    func: str
    # 额外元数据
    user: str
