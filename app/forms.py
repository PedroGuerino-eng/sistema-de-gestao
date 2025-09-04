from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, TextAreaField, SelectField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, EqualTo

class ClientForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField('Email', validators=[Optional(), Email()])
    telefone = StringField('Telefone', validators=[Optional()])
    notas = TextAreaField('Notas')
    submit = SubmitField('Salvar Cliente')

class ProductForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(min=2, max=120)])
    preco = DecimalField('Preço', validators=[DataRequired(), NumberRange(min=0)])
    estoque = IntegerField('Estoque', validators=[DataRequired(), NumberRange(min=0)])
    fornecedor = SelectField('Fornecedor', coerce=int, validators=[DataRequired()])
    descricao = TextAreaField('Descrição')
    submit = SubmitField('Salvar Produto')
    
class SupplierForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField('Email', validators=[Optional(), Email()])
    telefone = StringField('Telefone', validators=[Optional()])
    endereco = TextAreaField('Endereço', validators=[Optional()])
    submit = SubmitField('Salvar Fornecedor')
    
# --- NOVOS FORMULÁRIOS PARA A PÁGINA DE CONFIGURAÇÕES ---
class ChangePasswordForm(FlaskForm):
    nova_senha = PasswordField('Nova Senha', validators=[DataRequired(), Length(min=6)])
    confirmar_senha = PasswordField('Confirmar Nova Senha', validators=[DataRequired(), EqualTo('nova_senha', message='As senhas devem ser iguais.')])
    submit = SubmitField('Mudar Senha')

class ChangeEmailForm(FlaskForm):
    email = StringField('Novo Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Mudar Email')

class DeleteAccountForm(FlaskForm):
    confirmar = BooleanField('Eu entendo que esta ação é irreversível.', validators=[DataRequired()])
    submit = SubmitField('Deletar Minha Conta')