# mcm毕设

## 1.本地仓库管理

### 1.1 仓库物品筛选

### 1.2 仓库物品信息查询

### 1.3 物品入库

### 1.4 物品出库

## 2.物流管理

### 2.1 在途物资查询

### 2.2 路线规划

#### 2.2.1 地图处理

#### 2.2.2 约束条件设置

#### 2.2.3 耗时计算

### 2.3 物资申请

### 2.4 申请响应

```python
from pydantic import BaseModel


# 人员
class UserDB(BaseModel):
    # 人员唯一标识
    uuid: str
    # 密码hash盐
    salt: str
    # 密码加盐hash
    pwd: str
    # 权限
    pms: str
    # 扩展数据
    meta_data: dict

# 仓内货物
class ItemDB(BaseModel):
    # 货物唯一标识
    uuid: str
    # 舱内货物数量
    num: str
    # 舱内寻路
    loc: dict
    # 扩展元数据
    meta_data: dict


# 转运请求
class TaskDB(BaseModel):
    # 请求的唯一ID
    uuid: str
    # 站点ID
    site_id: str
    # 请求生成的时间戳
    time_stamp: str
    # 截至时间，非必须
    # deadline: str
    # 请求数量
    num: int
    # 请求物品id
    i_id: str


# 转运过程
class TransportDB(BaseModel):
    # 转运单位id
    uuid: str
    # 转运开始时间
    start_time: str
    # 完成进度
    progress: float
    # 预计到达时间
    init_eta: str
    # 当前预计到达时间
    current_eta: str


# 日志
class LogDB(BaseModel):
    # 日志唯一ID
    uuid: str
    # 等级
    status: str
    # 时间
    time_stamp: str
    # 产生日志方法
    func: str
    # 额外元数据
    meta_data: str
```
