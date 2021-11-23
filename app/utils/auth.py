import jwt
from datetime import datetime, timedelta
from flask import current_app, request, session
from functools import wraps
from app.utils.code import ResponseCode
from app.utils.util import ResMsg

class Auth(object):
    key = 'super-man$&123das%qzq'

    @classmethod
    def generate_access_token(cls, user_id, role, algorithm: str = 'HS256', exp: float = 1):
        """
        生成access_token
        :param user_id:自定义部分
        :param algorithm:加密算法
        :param exp:过期时间
        :return:
        """

        key = current_app.config.get('SECRET_KEY', cls.key)
        now = datetime.utcnow()
        exp_datetime = now + timedelta(hours=exp)
        access_payload = {
            'exp': exp_datetime,
            'flag': 0,  # 标识是否为一次性token，0是，1不是
            'iat': now,  # 开始时间
            'user_id': user_id,  # 自定义部分
            'role': role  # 自定义部分

        }
        access_token = jwt.encode(access_payload, key, algorithm=algorithm)
        return access_token

    @classmethod
    def generate_refresh_token(cls, user_id, role, algorithm: str = 'HS256', fresh: float = 1):
        """
        生成refresh_token

        :param user_id:自定义部分
        :param algorithm:加密算法
        :param fresh:过期时间
        :return:
        """
        key = current_app.config.get('SECRET_KEY', cls.key)

        now = datetime.utcnow()
        exp_datetime = now + timedelta(days=fresh)
        refresh_payload = {
            'exp': exp_datetime,
            'flag': 1,  # 标识是否为一次性token，0是，1不是
            'iat': now,  # 开始时间
            'user_id': user_id,  # 自定义部分
            'role': role # 自定义部分
        }

        refresh_token = jwt.encode(refresh_payload, key, algorithm=algorithm)
        return refresh_token

    @classmethod
    def encode_auth_token(cls, user_id: str,
                          role: int,
                          exp: float = 2,
                          fresh: float = 30,
                          algorithm: str = 'HS256') -> [str, str]:
        """
        :param user_id: 用户ID
        :param exp: access_token过期时间
        :param fresh:  refresh_token过期时间,刷新access_token使用
        :param algorithm: 加密算法
        :return:
        """
        access_token = cls.generate_access_token(user_id, role, algorithm, exp)
        refresh_token = cls.generate_refresh_token(user_id, role, algorithm, fresh)
        return access_token, refresh_token

    @classmethod
    def decode_auth_token(cls, token: str):
        """
        验证token
        :param token:
        :return:
        """
        key = current_app.config.get('SECRET_KEY', cls.key)
        try:
            # 取消过期时间验证
            # payload = jwt.decode(auth_token, config.SECRET_KEY, options={'verify_exp': False})
            payload = jwt.decode(token, key=key, algorithms="HS256")

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, jwt.InvalidSignatureError) as e:
            print(e)
            return None
        else:
            return payload

    def identify(self, auth_header):
        """
        用户鉴权
        :return: list
        """
        if auth_header:
            payload = self.decode_auth_token(auth_header)
            if payload is None:
                return False
            if "user_id" in payload and "flag" in payload:
                if payload["flag"] == 1:
                    # 用来获取新access_token的refresh_token无法获取数据
                    return False
                elif payload["flag"] == 0:

                    return (payload["user_id"], payload["role"])
                else:
                    # 其他状态暂不允许
                    return False
            else:
                return False
        else:
            return False


def login_required(f):
    """
    登陆保护，验证用户是否登陆
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        res = ResMsg()
        token = request.headers.get("Authorization", default=None)
        if not token:
            res.update(code=ResponseCode.NotLogin)
            return res.data

        auth = Auth()
        payload = auth.identify(token)
        if not payload:
            res.update(code=ResponseCode.NotLogin)
            return res.data
        user_id, role = payload
        # 获取到用户并写入到session中,方便后续使用
        session["user_id"] = user_id
        session["role"] = role

        return f(*args, **kwargs)

    return wrapper


def permission_required(permissions):
    """
    权限验证，验证用户是否有权操作
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            res = ResMsg()
            role = int(session['role'])
            if role not in permissions:
                res.update(ResponseCode.NoPrivilege)
                return res.data
            return f(*args, **kwargs)
        return wrapper
    return decorator