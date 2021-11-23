from enum import Enum


class ResponseCode(Enum):
    Success = 0  # 成功
    Fail = -1  # 失败
    NoResourceFound = 600           # 未找到资源
    InvalidParameter = 601          # 参数无效
    AccountOrPassWordError = 602    # 账户或密码错误
    AccountNotFound = 603           # 账户不存在
    NotLogin = 604                  # 请登陆后再访问
    NoPrivilege = 605               # 没有访问权限


class ResponseMessage(Enum):
    Success = "成功"
    Fail = "失败"
    NoResourceFound = "未找到资源"
    InvalidParameter = "参数错误"
    AccountOrPassWordError = "账户或密码错误"
    AccountNotFound = "账户不存在"
    NotLogin = "请登陆后再访问"
    NoPrivilege = "没有访问权限"
