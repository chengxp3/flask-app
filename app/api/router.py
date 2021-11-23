from app.api.user import bp as user_bp, UserApi

router = [
    user_bp,
    UserApi,
]