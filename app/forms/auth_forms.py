from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(message="O email é obrigatório."), Email(message="Forneça um email válido.")])
    password = PasswordField('Senha', validators=[DataRequired(message="A senha é obrigatória.")])
    submit = SubmitField('Entrar')

class RegisterForm(FlaskForm):
    name = StringField('Nome Completo', validators=[DataRequired(message="O nome é obrigatório.")])
    email = StringField('Email', validators=[DataRequired(message="O email é obrigatório."), Email(message="Forneça um email válido.")])
    password = PasswordField('Senha', validators=[DataRequired(message="A senha é obrigatória."), Length(min=6, message="A senha deve ter no mínimo 6 caracteres.")])
    submit = SubmitField('Cadastrar')
