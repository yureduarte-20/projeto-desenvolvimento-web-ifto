from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional

class UserCreateForm(FlaskForm):
    name = StringField('Nome Completo', validators=[DataRequired(message="O nome é obrigatório.")])
    email = StringField('Email', validators=[DataRequired(message="O email é obrigatório."), Email(message="Forneça um email válido.")])
    password = PasswordField('Senha', validators=[DataRequired(message="A senha é obrigatória."), Length(min=6, message="A senha deve ter no mínimo 6 caracteres.")])
    submit = SubmitField('Salvar')

class UserEditForm(FlaskForm):
    name = StringField('Nome Completo', validators=[DataRequired(message="O nome é obrigatório.")])
    email = StringField('Email', validators=[DataRequired(message="O email é obrigatório."), Email(message="Forneça um email válido.")])
    password = PasswordField('Nova Senha (opcional)', validators=[Optional(), Length(min=6, message="A senha deve ter no mínimo 6 caracteres.")])
    submit = SubmitField('Atualizar')
