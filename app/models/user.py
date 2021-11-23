from enum import Enum
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.ext.hybrid import hybrid_property
from app.utils.core import db
from app.utils.util import gen_uuid


User_List = [
    {
        'username':"admin",
        'password':"Admin123",
        'nickname':"管理员",
        'role':1,
    },
]


class Role(Enum):
    Guest = 0       # 访客，默认创建的用户，无任何权限
    SuperAdmin = 1  # 超级管理员，全部权限
    Admin = 2       # 普通管理员，部门级全部权限
    Auditor = 3     # 维护人员，部门级维护权限
    Reader = 4        # 普通人员，部门级查看权限


def check_password(hash, passwd):
    return check_password_hash(hash, passwd)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.String(16), default=gen_uuid, primary_key=True)
    username = db.Column(db.String(16), unique=True, nullable=False)
    _password = db.Column(db.String(128), name="password", nullable=False)
    nickname = db.Column(db.String(32), nullable=True)
    role = db.Column(db.Integer, nullable=False, default=Role.Guest)
    enable = db.Column(db.Boolean, nullable=False, default=True)
    create_time = db.Column(db.DateTime, default=datetime.now)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = generate_password_hash(value)

    def check_password_hash(self, password):
        return check_password_hash(self._password, password)

def init():
    """Create a new admin user"""
    record = db.session.query(User).filter(User.username == 'admin').first()
    if not record:
        for item in User_List:
            user = User(username=item['username'], password=item['password'], nickname=item['nickname'],  role=item['role'])
            db.session.add(user)

        db.session.commit()
        print('User init')
