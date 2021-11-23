from app.factory import create_app
from waitress import serve
from paste.translogger import TransLogger

# ## PROD
app = create_app(config_name="PRODUCTION")
app.app_context().push()

# if __name__ == "__main__":
serve(TransLogger(app, setup_console_handler=False), host="0.0.0.0", port=3000)

