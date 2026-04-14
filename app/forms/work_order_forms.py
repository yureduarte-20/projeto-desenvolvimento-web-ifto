from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length

class WorkOrderForm(FlaskForm):
    # Fieldset 1: Dados do solicitante
    requester_name = StringField('Nome', validators=[DataRequired(message="O nome é obrigatório.")])
    requester_email = StringField('Email', validators=[DataRequired(message="O email é obrigatório."), Email(message="Forneça um email válido.")])
    requester_phone = StringField('Celular / Telefone', validators=[DataRequired(message="O telefone é obrigatório.")])
    requester_document = StringField('CPF / CNPJ', validators=[DataRequired(message="O documento é obrigatório.")])

    # Fieldset 2: Dados da OS
    description = TextAreaField('Descrição do Problema', validators=[DataRequired(message="A descrição do problema é obrigatória."), Length(min=10, message="A descrição deve ter no mínimo 10 caracteres.")])
    estimated_delivery_date = DateField('Data Estimada de Entrega', format='%Y-%m-%d', validators=[Optional()])

    submit = SubmitField('Abrir Ordem de Serviço')
