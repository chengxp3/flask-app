import re
from functools import wraps
import uuid
from flask import jsonify
from app.utils.response import ResMsg

def gen_uuid():
    return uuid.uuid4().hex[:16]

def gen_suuid():
    return uuid.uuid4().hex[:4]

def route(bp, *args, **kwargs):
    """
    路由设置,统一返回格式
    :param bp: 蓝图
    :param args:
    :param kwargs:
    :return:
    """
    kwargs.setdefault('strict_slashes', False)

    def decorator(f):
        @bp.route(*args, **kwargs)
        @wraps(f)
        def wrapper(*args, **kwargs):
            rv = f(*args, **kwargs)
            # 响应函数返回整数和浮点型
            if isinstance(rv, (int, float)):
                res = ResMsg()
                res.update(data=rv)
                return jsonify(res.data)
            # 响应函数返回元组
            elif isinstance(rv, tuple):
                # 判断是否为多个参数
                if len(rv) >= 3:
                    return jsonify(rv[0]), rv[1], rv[2]
                else:
                    return jsonify(rv[0]), rv[1]
            # 响应函数返回字典
            elif isinstance(rv, dict):
                return jsonify(rv)
            # 响应函数返回字节
            elif isinstance(rv, bytes):
                rv = rv.decode('utf-8')
                return jsonify(rv)
            else:
                return jsonify(rv)

        return wrapper

    return decorator


def view_route(f):
    """
    路由设置,统一返回格式
    :param f:
    :return:
    """

    def decorator(*args, **kwargs):
        rv = f(*args, **kwargs)
        if isinstance(rv, (int, float)):
            res = ResMsg()
            res.update(data=rv)
            return jsonify(res.data)
        elif isinstance(rv, tuple):
            if len(rv) >= 3:
                return jsonify(rv[0]), rv[1], rv[2]
            else:
                return jsonify(rv[0]), rv[1]
        elif isinstance(rv, dict):
            return jsonify(rv)
        elif isinstance(rv, bytes):
            rv = rv.decode('utf-8')
            return jsonify(rv)
        else:
            return jsonify(rv)

    return decorator


def obj_to_json(obj):
    out = obj.__dict__
    for name in obj.__mapper__.relationships.keys():
        tmp = getattr(obj, name).__dict__
        if '_sa_instance_state' in tmp:
            tmp.pop('_sa_instance_state')
            out[name] = tmp

    if '_sa_instance_state' in out.keys():
        out.pop("_sa_instance_state")

    return out


def parse_data(data, model):
    if data:
        if isinstance(data, (list, tuple)):
            data = [obj_to_json(item) for item in data]
        else:
            data = obj_to_json(data)
    return data


def check_pwd_reg(pwd):
    v_pwd = re.match(r'^(?:(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])).{6,18}$', pwd)
    if v_pwd is None:
        return False
    else:
        return True


class PhoneTool(object):
    """
    手机号码验证工具
    """
    @staticmethod
    def check_phone(phone: str):
        if len(str(phone)) == 11:
            # v_phone = re.match(r"\d{11}", phone)
            v_phone = re.match(r'^1[3-9][0-9]{9}$', phone)
            if v_phone is None:
                return None
            else:
                phone = v_phone.group()

                return phone
        else:
            return None

from decimal import *
from sqlalchemy.types import TypeDecorator, Integer

# sqlite不支持Decimal，自定义 sqlalchemy Decimal类
class SqliteDecimal(TypeDecorator):
    impl = Integer
    cache_ok = True
    def __init__(self, scale):
        TypeDecorator.__init__(self)
        self.scale = scale
        self.multiplier_int = Decimal(10 ** self.scale)

    def process_bind_param(self, value, dialect):
        if value is not None and len(str(value).strip()):
            value = int(Decimal(value) * self.multiplier_int)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = Decimal(Decimal(value) / self.multiplier_int)
        return value
