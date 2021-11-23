import logging
from flask import Blueprint, session, request

import traceback
from app.utils.auth import Auth, login_required, permission_required
from app.utils.code import ResponseCode
from app.utils.response import ResMsg
from app.utils.core import db
from app.utils.util import check_pwd_reg
from app.api.base import Service


from app.models.user import User, Role

bp = Blueprint("user", __name__, url_prefix="/api/user")

logger = logging.getLogger(__name__)

@bp.route('login', methods=['POST'])
def login():
    res = ResMsg()
    try:
        obj = request.get_json(force=True)
        username = obj.get('username')
        password = obj.get('password')

        if not obj or not username or not password:
            res.update(code=ResponseCode.InvalidParameter)
            return res.data

        user = db.session.query(User).filter(User.username == username).first()
        if not user:
            res.update(code=ResponseCode.AccountNotFound)
            return res.data

        if not user.check_password_hash(password):
            res.update(code=ResponseCode.AccountOrPassWordError)
            return res.data

        access_token, refresh_token = Auth.encode_auth_token(user_id=user.id, role=user.role)

        res.update(data={
            'access_token': access_token,
            'refresh_token': refresh_token,
            'username': username,
            'role': user.role,
            'nickname': user.nickname
        })
        return res.data

    except Exception as e:
        traceback.print_exc()
        res.update(code=ResponseCode.Fail)
        return res.data

@bp.route('logout', methods=['GET'])
@login_required
def logout():
    res = ResMsg()
    session.pop('user_id', None)
    return res.data


@bp.route('password', methods=['PUT'])
@login_required
def modify_password():
    res = ResMsg()
    try:
        obj = request.get_json(force=True)

        user_id = session.get('user_id')
        old_password = obj.get('oldPwd')
        password = obj.get('password')
        check_pwd = obj.get('checkPwd')

        if not user_id or not old_password or not password or not check_pwd:
            res.update(code=ResponseCode.AccountNotFound)
            return res.data

        user = User.query.filter(User.id == user_id).first()
        if not user:
            res.update(code=ResponseCode.AccountNotFound)
            return res.data

        old_password_check = user.check_password_hash(old_password)
        if not old_password_check or password != check_pwd or not check_pwd_reg(password):
            res.update(code=ResponseCode.InvalidParameter)
            return res.data

        user.password = password
        db.session.add(user)
        db.session.commit()
        return res.data

    except Exception as e:
        traceback.print_exc()
        res.update(code=ResponseCode.Fail)
        return res.data


@bp.route('reset', methods=['POST'])
@login_required
def reset_password():
    pass


@bp.route('enable', methods=['POST'])
@login_required
@permission_required([Role.Admin, Role.SuperAdmin])
def enable():
    pass


@bp.route('/permission', methods=['GET'])
@login_required
@permission_required([Role.Admin, Role.SuperAdmin])
def permission():
    res = ResMsg()
    try:
        user_id = session.get("user_id")
        role = Role(int(session.get("role")))
        if role not in [Role.Admin, Role.SuperAdmin]:
            res.update(code=ResponseCode.NoPrivilege)
            return res.data
        return res.data
    except Exception as e:
        traceback.print_exc()
        res.update(code=ResponseCode.Fail)
        return res.data


class UserApi(Service):
    __model__ = User
    service_name = 'user'
    __methods__ = ['GET', 'POST', 'PUT', 'DELETE']

    @login_required
    def get(self, key=None):
        res = ResMsg()
        user_id = session.get("user_id")

        page = request.args.get("page")
        size = request.args.get("size")
        if not page and not size :
            return super(UserApi, self).get(user_id)

        return super(UserApi, self).get(key)


    def _add_query_expr(self, query, by):
        department = session.get('department')
        role = session.get('role')
        query.append(User.role >= role)

        if department is not None and department != '0' and role not in [Role.SuperAdmin, Role.Admin]:
            query.append(User.department.in_(department.split(',')))


    def _add_more_info(self, query, data):
        if '_password' in data:
            data.pop('_password')

        else:
            for user in data['list']:
                user.pop('_password')

    def _put_check(self, data):
        print(data)
