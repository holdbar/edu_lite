import re
from flask_wtf import Form
from wtforms import BooleanField, StringField, PasswordField, FileField, SelectField, RadioField, SelectMultipleField, widgets
from wtforms.fields.html5 import DateField
from wtforms.validators import Email, DataRequired, EqualTo, ValidationError, InputRequired, Required
from edu_lite import db
from .models import Students, Answers, Questions, Tests, Attempts
from passlib.hash import sha256_crypt


def exists_user(form, field):
    """
    Username validator.
    
    Checks if user exists in base with name.
    """

    user = Students.query.filter_by(name=field.data).first()
    if not user:
        raise ValidationError('There is no user with name {}'.format(field.data))


def validate_username(form, field):
    """
    Username already in use validator.

    Count the number of user ids for that username
    if it's not 0, there's a user with that username already.
    """

    if db.session.query(db.func.count(Students.id)).filter_by(name=field.data).scalar():
        raise ValidationError('Name already in use')



class TestForm(Form):
    """Test form."""

    test = SelectField('Тест', choices=[])



class LoginForm(Form): 
    """Login form."""

    name = StringField('Имя', validators=[DataRequired(), exists_user])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня", default=False)

    def validate_user(self, form_name, form_password):
        """User authorization check."""

        user = Students.query.filter_by(name=form_name).first()
        if user:
            base_password = user.password
            if sha256_crypt.verify(form_password, base_password) == True:
                return user
            else:
                raise ValidationError('Wrong password')


class RegistrationForm(LoginForm):
    """Registration form."""

    name = StringField('Имя', validators=[DataRequired(), validate_username])
    password_repeat = PasswordField('Повтор пароля', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])

    def register_user(self, form_name, form_password):
        """User registration."""

        crypt_password = sha256_crypt.hash(form_password)
        new_user = Students(form_name, crypt_password, 0)  
        db.session.add(new_user)
        db.session.commit()

class MultiCheckboxField(SelectMultipleField):
    """Field for multi answers."""

    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class AttemptForm(Form):
    """Form for pass atempt."""

    answer = RadioField('answer', choices=[], validators=[Required()])
    multi_answer = MultiCheckboxField('multi_answer', choices=[], validators=[Required()])

    def add_choices(self, question_id):
        """Load choices."""

        answers = [(a.id,a.value) for a in Answers.query.filter_by(question_id=question_id).all()]
        self.answer.choices = answers
        self.answer.id = question_id
        self.answer.name= str(question_id)
        return ''

    def add_multiple_choices(self, question_id):
        """Load multiple choices."""

        answers = [(a.id,a.value) for a in Answers.query.filter_by(question_id=question_id).all()]
        self.multi_answer.choices = answers
        self.multi_answer.id = question_id
        self.multi_answer.name= str(question_id)
        return ''


class PastAttemptsForm(TestForm):
    """Past attempts form."""

    student = SelectField('Студент', choices=[])
    date = DateField('Дата', format="%Y-%m-%d")



class FileForm(TestForm):
    """File form."""

    file = FileField('Файл', validators=[DataRequired()])

class NewTestForm(Form):
    """New test form."""

    test_name = StringField('Название теста', validators=[DataRequired()])

