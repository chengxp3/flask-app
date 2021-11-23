import os, sys
import yaml
import logging
import logging.config
from flask_cors import CORS
from flask import Flask, Blueprint
from app.api.router import router
from app.utils.core import JSONEncoder, db, migrate
from app.models.user import init as user_init, User

if getattr(sys, 'frozen', None):
    basedir = sys._MEIPASS  # pyinstaller打包后用的这个路径
else:
    basedir = os.getcwd()

exec_dir = os.getcwd()

print('base dir: ', basedir)
print('exec dir : ', exec_dir)

def create_app(config_name="PRODUCTION"):

    config_path = os.path.join(exec_dir, 'conf/config.yml')

    conf = read_yaml(config_name, config_path)
    conf['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/db/app.db'.format(exec_dir)

    app = Flask(__name__, template_folder=os.path.join(basedir, conf['TEMPLATE_FOLDER']), static_folder=os.path.join(basedir, conf['STATIC_FOLDER']), static_url_path="")
    CORS(app, resources={r'/*': {'origins': '*'}}, supports_credentials=True)

    app.config.update(conf)

    # 映射static目录下的SPA应用
    register_web(app)
    register_api(app, router)

    # 返回json格式转换
    app.json_encoder = JSONEncoder

    # 注册数据库连接
    db.app = app
    db.init_app(app)
    migrate.init_app(app, db)
    # 日志文件目录
    if not os.path.exists(app.config['LOGGING_PATH']):
        os.mkdir(app.config['LOGGING_PATH'])

    # 日志设置
    with open(app.config['LOGGING_CONFIG_PATH'], 'r', encoding='utf-8') as f:
        dict_conf = yaml.safe_load(f.read())
    logging.config.dictConfig(dict_conf)

    # 数据库数据初始化
    engine = db.get_engine()
    is_init = User.metadata.tables[User.__tablename__].exists(engine)
    if is_init:
        db_init()
    return app


def read_yaml(config_name, config_path):
    if config_name and config_path:
        with open(config_path, 'r', encoding='utf-8') as f:
            conf = yaml.safe_load(f.read())
        if config_name in conf.keys():
            return conf[config_name.upper()]
        else:
            raise KeyError('未找到对应的配置信息')
    else:
        raise ValueError('请输入正确的配置名称或配置文件路径')

def register_web(app):

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return app.send_static_file("index.html")

    @app.errorhandler(404)
    def not_found(e):
        return app.send_static_file("index.html")


def register_api(app, routers):
    for router_api in routers:
        if isinstance(router_api, Blueprint):
            app.register_blueprint(router_api)
        else:
            try:
                endpoint = router_api.__name__
                view_func = router_api.as_view(endpoint)
                # 如果没有服务名,默认 类名小写
                if hasattr(router_api, "service_name"):
                    url = '/api/{}'.format(router_api.service_name.lower())
                else:
                    url = '/api/{}'.format(router_api.__name__.lower())

                if 'GET' in router_api.__methods__:
                    app.add_url_rule(url, defaults={'key': None}, view_func=view_func, methods=['GET', ])
                    # app.add_url_rule('{}/<string:key>'.format(url), view_func=view_func, methods=['GET', ])

                if 'POST' in router_api.__methods__:
                    app.add_url_rule(url, view_func=view_func, methods=['POST', ])

                if 'PUT' in router_api.__methods__:
                    app.add_url_rule('{}/<string:key>'.format(url), view_func=view_func, methods=['PUT', ])

                if 'DELETE' in router_api.__methods__:
                    app.add_url_rule('{}/<string:key>'.format(url), view_func=view_func, methods=['DELETE', ])

            except Exception as e:
                raise ValueError(e)

def db_init():
    try:
        user_init()
    except Exception as e:
        raise ValueError(e)