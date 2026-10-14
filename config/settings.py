INSTALLED_APPS = [
    # ... стандартные приложения
    'quests',
]

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
