from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models.user import User
from app.forms import UserCreateForm, UserEditForm

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/')
@login_required
def list():
    users = User.query.order_by(User.id.desc()).all()
    return render_template('users/list.html', users=users)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = UserCreateForm()
    
    if form.validate_on_submit():
        # Verificar se email já existe
        if User.query.filter_by(email=form.email.data).first():
            flash('Este email já está em uso.', 'danger')
            return redirect(url_for('users.create'))

        user = User(name=form.name.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('users.list'))
        
    return render_template('users/create.html', form=form)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    user = User.query.get_or_404(id)
    form = UserEditForm(obj=user)
    
    if form.validate_on_submit():
        # Verificar se novo email já existe em outro usuário
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user and existing_user.id != id:
            flash('Este email já está em uso por outro usuário.', 'danger')
            return redirect(url_for('users.edit', id=id))

        user.name = form.name.data
        user.email = form.email.data
        if form.password.data:  # Atualizar senha apenas se for fornecida
            user.set_password(form.password.data)
            
        db.session.commit()

        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('users.list'))
        
    return render_template('users/edit.html', user=user, form=form)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    
    flash('Usuário removido com sucesso!', 'success')
    return redirect(url_for('users.list'))

