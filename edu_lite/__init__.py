from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config.from_object('config.Config')


# инициализируем объект БД
db = SQLAlchemy(app)

dtb = DebugToolbarExtension(app)

from edu_lite import views


Bootstrap(app)


# подключаем плагин авторизации
from flask_login import LoginManager, current_user

# Инициализируем его и задаем действие "входа"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Задаем обработчик, возвращающий пользователя по Id, либо None. Здесь пользователь запрашивается из базы.
@login_manager.user_loader
def load_user(userid):
    from .models import Students
    return Students.query.get(int(userid))




