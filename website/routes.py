from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from . import db
from .models import Clinica, User, Pet
from .forms import RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# Definindo o Blueprint
routes = Blueprint('routes', __name__)

# Página inicial
@routes.route('/')
def welcome():
    return render_template('welcome.html')

# Função auxiliar para salvar no banco de dados
def save_to_db(instance):
    try:
        db.session.add(instance)
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao salvar no banco de dados: {e}")
        return False

# Parâmetros de limite de tentativas e tempo de bloqueio
MAX_ATTEMPTS = 5
LOCKOUT_TIME = 300  # Tempo de bloqueio em segundos (5 minutos)

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        # Buscar o usuário no banco de dados pelo email
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('Usuário não encontrado. Verifique o email digitado.', 'danger')
            return render_template('login.html')  # Retorna a página de login

        # Verifica se o usuário foi bloqueado
        if user.failed_attempts is None:
            user.failed_attempts = 0  # Caso falte um valor no campo, vamos garantir que seja 0.

        if user.failed_attempts >= MAX_ATTEMPTS:
            if user.lockout_time is None or (datetime.now() - user.lockout_time).seconds >= LOCKOUT_TIME:
                # Desbloqueia o usuário
                user.failed_attempts = 0
                user.lockout_time = None
                db.session.commit()
            else:
                # Usuário ainda está bloqueado
                flash('Sua conta foi bloqueada devido a tentativas de login excessivas. Tente novamente mais tarde.', 'danger')
                return render_template('login.html')

        # Verifica a senha
        if not check_password_hash(user.senha, senha):
            user.failed_attempts += 1  # Incrementa as tentativas falhas

            if user.failed_attempts >= MAX_ATTEMPTS:
                # Bloqueia o usuário após falhar muitas vezes
                user.lockout_time = datetime.now()  # Define o bloqueio
                flash('Muitas tentativas falhas. Sua conta foi bloqueada por 5 minutos.', 'danger')
            else:
                flash(f'Senha inválida. Você tem {MAX_ATTEMPTS - user.failed_attempts} tentativa(s) restante(s).', 'danger')
            
            db.session.commit()
            return render_template('login.html')

        # Login bem-sucedido
        user.failed_attempts = 0  # Zera as tentativas falhas
        user.lockout_time = None  # Limpa o bloqueio
        db.session.commit()

        session['user_id'] = user.id  # Salva o ID do usuário na sessão

        if not user.pets:
            return redirect(url_for('routes.register_pet'))
        else:
            last_pet = user.pets[-1]  # Assume pets ordenados
            return redirect(url_for('routes.initial', pet_id=last_pet.id))

    return render_template('login.html')


# Cadastro de usuário
@routes.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()  # Carrega o formulário

    if form.validate_on_submit():
        if form.senha.data != form.confirmar_senha.data:
            flash('As senhas não coincidem. Tente novamente.', 'danger')
            return redirect(url_for('routes.register'))

        usuario = form.usuario.data
        email = form.email.data
        senha = form.senha.data

        if User.query.filter_by(usuario=usuario).first():
            flash('Este nome de usuário já está em uso. Escolha outro.', 'danger')
            return redirect(url_for('routes.register'))

        if User.query.filter_by(email=email).first():
            flash('Este email já está registrado. Use outro.', 'danger')
            return redirect(url_for('routes.register'))

        hashed_password = generate_password_hash(senha, method='pbkdf2:sha256')
        new_user = User(usuario=usuario, email=email, senha=hashed_password)

        if save_to_db(new_user):
            flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('routes.login'))
        else:
            flash('Erro ao cadastrar. Tente novamente mais tarde.', 'danger')

    return render_template('register.html', form=form)


# Cadastro de clínica
def create_clinica(nome, email, senha):
    hashed_password = generate_password_hash(senha, method='pbkdf2:sha256')
    new_clinica = Clinica(nome=nome, email=email, senha=hashed_password)
    
    try:
        db.session.add(new_clinica)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao cadastrar a clínica: {e}")
        return False

@routes.route('/register-clinica', methods=['GET', 'POST'])
def register_clinica():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')

        if senha != confirmar_senha:
            flash('As senhas não coincidem. Tente novamente.', 'danger')
            return redirect(url_for('routes.register_clinica'))

        clinica_existente = Clinica.query.filter_by(email=email).first()
        if clinica_existente:
            flash('Este email já está registrado. Escolha outro.', 'danger')
            return redirect(url_for('routes.register_clinica'))

        if create_clinica(nome, email, senha):
            flash('Cadastro da clínica realizado com sucesso!', 'success')
            return redirect(url_for('routes.login'))
        else:
            flash('Erro ao cadastrar a clínica. Tente novamente mais tarde.', 'danger')

    return render_template('registerClinica.html')



# Cadastro de PET
@routes.route('/register-pet', methods=['GET', 'POST'])
def register_pet():
    if request.method == 'POST':
        nome = request.form.get('nome')
        idade = request.form.get('idade')
        peso = request.form.get('peso')
        tipo = request.form.get('tipo')
        raca_genero = request.form.get('raca_genero')

        if not nome or not idade or not peso or not tipo or not raca_genero:
            flash('Todos os campos são obrigatórios. Por favor, preencha todos.', 'danger')
            return redirect(url_for('routes.register_pet'))

        new_pet = Pet(
            nome=nome,
            idade=idade,
            peso=peso,
            tipo=tipo,
            raca_genero=raca_genero,
            user_id=session.get('user_id')
        )

        if save_to_db(new_pet):
            return redirect(url_for('routes.confirmation_pet', pet_id=new_pet.id))

    return render_template('registerPETT.html')


@routes.route('/confirmation-pet', methods=['GET'])
def confirmation_pet():
    user_id = session.get('user_id')
    if user_id:
        # Busca todos os pets do usuário logado
        pets = Pet.query.filter_by(user_id=user_id).all()
        if pets:
            return render_template('confirmationPetInfo.html', pets=pets)
        else:
            flash('Você não tem nenhum pet cadastrado.', 'warning')
            return redirect(url_for('routes.register_pet'))
    else:
        flash('Acesso negado ou usuário não encontrado.', 'danger')
        return redirect(url_for('routes.register_pet'))



@routes.route('/delete-pet/<int:pet_id>', methods=['POST'])
def delete_pet(pet_id):
    pet = Pet.query.get(pet_id)
    if pet and pet.user_id == session.get('user_id'):
        db.session.delete(pet)
        db.session.commit()
        flash('Pet excluído com sucesso!', 'success')
    else:
        flash('Acesso negado ou pet não encontrado.', 'danger')
    return redirect(url_for('routes.confirmation_pet'))


@routes.route('/initial')
def initial():
    return render_template('initial.html')

# Protocolo
@routes.route('/protocolo')
def protocolo():
    return render_template('protocolo.html')