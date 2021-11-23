from app.factory import create_app

## DEV
app = create_app(config_name="DEVELOPMENT")
app.app_context().push()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)