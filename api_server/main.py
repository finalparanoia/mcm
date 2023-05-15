from fastapi import FastAPI, HTTPException, Depends
from fastapi import status
from bll.auth import UserAuth
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from lib.lib import Libs
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dto.dto import RegUser, Item, Task, Transport
from bll.bll import BLL
from bll.log import Log


# 设置登录及验证路径
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token/")

# 实例化相关类
lib = Libs()
app = FastAPI()
ua = UserAuth()
log = Log()
bll = BLL()


# 设置密钥生成策略
server_key = "114514"
algorithm = "HS256"
alive_time = 60

# 设置跨域访问安全策略
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 生成令牌
def create_jwt_token(data: dict, expire_delta: Optional[timedelta] = None):
    # 如果传入了过期时间, 那么就是用该时间, 否则使用默认的时间
    expire = datetime.utcnow() + expire_delta if expire_delta else datetime.utcnow() + timedelta(days=alive_time)
    # 需要加密的数据data必须为一个字典类型, 在数据中添加过期时间键值对, 键exp的名称是固定写法
    data.update({'exp': expire})
    # 进行jwt加密
    token = jwt.encode(claims=data, key=server_key, algorithm=algorithm)
    return token


# 产生HTTP异常
def exp():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="认证失败",
        # 根据OAuth2规范, 认证失败需要在响应头中添加如下键值对
        headers={'WWW-Authenticate': "Bearer"}
    )


# 检验令牌有效性
def verify_token(token: str):
    try:
        payload = jwt.decode(token=token, key=server_key, algorithms=[algorithm])
        username = payload.get('username')
        if not username:
            return False, ""
        else:
            return True, username
    except JWTError:
        return False, ""


# 提供HTTP探针，检测服务器运行状态
@app.get("/test/")
async def test_api():
    return {
        "name": "API Server",
        "version": "0.0.1",
        "status": "running",
        "status_code": 0,
    }


# 注册账户的HTTP接口
@app.post("/account/")
async def reg_api(data: RegUser):
    status_bool, uuid = ua.reg(data)
    return {"status": status_bool, "username": uuid}


# 登录以获取令牌的HTTP接口
@app.post("/token/")
async def login_api(form_data: OAuth2PasswordRequestForm = Depends()):
    # 1、获取客户端传过来的用户名、密码
    username = form_data.username
    password = form_data.password
    # 2、模拟从数据库中根据用户名查找对应的用户
    if ua.auth(username, password):
        data = {'username': username}
        token = create_jwt_token(data)
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名或密码不正确")


# 检测令牌有效性的HTTP接口
@app.get("/token/")
async def test_token_api(token: str = Depends(oauth2_scheme)):
    resp_bool, username = verify_token(token)
    if resp_bool:
        return {"status": True, "info": "Authorized Access", "username": username}
    else:
        exp()


# 管理员获取全部账户的接口
@app.get("/all/")
async def all_api(token: str = Depends(oauth2_scheme)):
    resp_bool, username = verify_token(token)
    if resp_bool:
        if ua.verify_admin(username):
            return {"status": True, "data": ua.all()}
        else:
            return {"status": False, "data": []}
    else:
        exp()


# 修改账户的HTTP接口
@app.put("/profile/")
async def update_profile_api(profile: RegUser, token: str = Depends(oauth2_scheme)):
    resp_bool, username = verify_token(token)
    if resp_bool:
        profile_dict = profile.dict()
        profile_dict["username"] = username
        return ua.update(profile_dict)
    elif ua.verify_admin(username):
        return ua.update(profile.dict())
    else:
        exp()


# 删除账户的HTTP接口
@app.delete("/account/{target_username}/")
async def delete_profile_api(target_username: str, token: str = Depends(oauth2_scheme)):
    resp_bool, username = verify_token(token)
    if resp_bool:
        if ua.verify_admin(username):
            return ua.delete(target_username)
        else:
            return {"status": False, "info": "not admin"}
    else:
        exp()


# 创建物品
@app.post("/item/")
async def item_create_api(r: Item, token: str = Depends(oauth2_scheme)):
    resp_bool, username = verify_token(token)
    if resp_bool:
        bll.create_item(r)
        return {"status": 6}
    else:
        exp()


# 查询物品
@app.get("/item/by_uuid/{uuid}/")
async def item_create_api(uuid: str, token: str = Depends(oauth2_scheme)):
    resp_bool, username = verify_token(token)
    if resp_bool:
        return bll.read_item(uuid)
    else:
        exp()


# 查询物品
@app.get("/item/by_name/{name}/")
async def item_query_api(name: str, token: str = Depends(oauth2_scheme)):
    resp_bool, username = verify_token(token)
    if resp_bool:
        return bll.query_item(name)
    else:
        exp()


# 修改数量物品
@app.put("/item/{uuid}/{num}/")
async def item_update_api(uuid: str, num: int, token: str = Depends(oauth2_scheme)):
    resp_bool, username = verify_token(token)
    if resp_bool:
        return bll.update_item(uuid, num)
    else:
        exp()


# 创建任务
@app.post("/task/")
async def task_create_api(t: Task, token: str = Depends(oauth2_scheme)):
    resp_bool, username = verify_token(token)
    if resp_bool:
        return {"uuid": bll.create_task(t)}
    else:
        exp()


# 获取任务
@app.get("/task/{uuid}/")
async def task_create_api(uuid: str, token: str = Depends(oauth2_scheme)):
    resp_bool, username = verify_token(token)
    if resp_bool:
        return bll.read_task(uuid)
    else:
        exp()


# 获取全部任务
@app.get("/task/all/")
async def task_create_api(token: str = Depends(oauth2_scheme)):
    resp_bool, username = verify_token(token)
    if resp_bool:
        return bll.all_task()
    else:
        exp()


# 修改任务状态
@app.put("/task/{uuid}/{task_status}/")
async def task_create_api(uuid: str, task_status: str, token: str = Depends(oauth2_scheme)):
    resp_bool, username = verify_token(token)
    if resp_bool:
        bll.update_task(uuid, task_status)
        return {"status": True}
    else:
        exp()


# 创建运输
@app.post("/trans/")
async def trans_create_api(t: Transport, token: str = Depends(oauth2_scheme)):
    resp_bool, username = verify_token(token)
    if resp_bool:
        bll.create_transport(t, username)
        return {"status": True}
    else:
        exp()


# 修改运输状态
@app.put("/trans/{uuid}/{trans_status}/")
async def task_create_api(uuid: str, trans_status: str, token: str = Depends(oauth2_scheme)):
    resp_bool, username = verify_token(token)
    if resp_bool:
        bll.update_transport(uuid, trans_status)
        return {"status": True}
    else:
        exp()


# 查询运输状态
@app.put("/trans/all/")
async def task_create_api(token: str = Depends(oauth2_scheme)):
    resp_bool, username = verify_token(token)
    if resp_bool:
        return bll.all_transport()
    else:
        exp()


@app.get("/level/")
async def get_level_api(token: str = Depends(oauth2_scheme)):
    resp_bool, username = verify_token(token)
    if resp_bool:
        return {"admin": ua.verify_admin(username)}
    else:
        exp()


if __name__ == "__main__":
    from uvicorn import run
    run(app="main:app", port=8000, host="::", workers=4)
