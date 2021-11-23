环境：
python3.6+，NodeJs v7+，并安装cnpm

后端接口目录 app/api
后端数据库类目录 app/models
后端数据文件（sqlite）app/app.db
参考接口类 app/api/user.py
新增接口，需要将接口或者Service类添加到 app/api/router的数组中

安装python依赖包：
在项目根目录 执行
pip3 install -r requirements.txt

执行python后端：
在项目根目录 执行
python3 dev.py

生成migrations/db，执行
flask db init
flask db migrate -m "Initial migration."
flask db upgrade

web端开发目录 web
打包后web输出目录 static/

安装web依赖包：
在项目根目录/web 目录下执行
cnpm install 

执行web端：
在项目根目录/web 目录下执行
npm run serve
