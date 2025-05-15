from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session, jsonify
from . import db
from .models import Clinica, User, Pet, Vacina, Tratamento, Vermifugo, Exame
from .forms import RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

routes = Blueprint("routes", __name__)


@routes.route("/")
def welcome():
    return render_template("welcome.html")


def save_to_db(instance):
    try:
        db.session.add(instance)
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao salvar no banco de dados: {e}")
        return False


MAX_ATTEMPTS = 5
LOCKOUT_TIME = 300


@routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Usuário não encontrado. Verifique o email digitado.", "danger")
            return render_template("login.html")

        if user.failed_attempts is None:
            user.failed_attempts = 0

        if hasattr(user, 'lockout_time') and user.lockout_time and user.failed_attempts >= MAX_ATTEMPTS:
            if (datetime.now() - user.lockout_time).seconds >= LOCKOUT_TIME:
                user.failed_attempts = 0
                user.lockout_time = None
                db.session.commit()
            else:
                flash("Sua conta foi bloqueada devido a tentativas de login excessivas. Tente novamente mais tarde.",
                      "danger")
                return render_template("login.html")
        elif user.failed_attempts >= MAX_ATTEMPTS and (not hasattr(user, 'lockout_time') or not user.lockout_time):
            user.lockout_time = datetime.now()
            db.session.commit()
            flash("Muitas tentativas falhas. Sua conta foi bloqueada por 5 minutos.", "danger")
            return render_template("login.html")

        if not check_password_hash(user.senha, senha):
            user.failed_attempts += 1
            if user.failed_attempts >= MAX_ATTEMPTS:
                user.lockout_time = datetime.now()
                flash("Muitas tentativas falhas. Sua conta foi bloqueada por 5 minutos.", "danger")
            else:
                flash(f"Senha inválida. Você tem {MAX_ATTEMPTS - user.failed_attempts} tentativa(s) restante(s).",
                      "danger")
            db.session.commit()
            return render_template("login.html")

        user.failed_attempts = 0
        user.lockout_time = None
        db.session.commit()
        session["user_id"] = user.id

        # Após o login, o usuário é direcionado para a página inicial.
        return redirect(url_for("routes.initial"))

    return render_template("login.html")


@routes.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.senha.data != form.confirmar_senha.data:
            flash("As senhas não coincidem. Tente novamente.", "danger")
            return redirect(url_for("routes.register"))
        usuario = form.usuario.data
        email = form.email.data
        senha = form.senha.data
        if User.query.filter_by(usuario=usuario).first():
            flash("Este nome de usuário já está em uso. Escolha outro.", "danger")
            return redirect(url_for("routes.register"))
        if User.query.filter_by(email=email).first():
            flash("Este email já está registrado. Use outro.", "danger")
            return redirect(url_for("routes.register"))
        hashed_password = generate_password_hash(senha, method="pbkdf2:sha256")
        new_user = User(usuario=usuario, email=email, senha=hashed_password)
        if save_to_db(new_user):
            flash("Cadastro realizado com sucesso! Faça login para continuar.", "success")
            return redirect(url_for("routes.login"))
        else:
            flash("Erro ao cadastrar. Tente novamente mais tarde.", "danger")
    return render_template("register.html", form=form)


def create_clinica(nome, email, senha):
    hashed_password = generate_password_hash(senha, method="pbkdf2:sha256")
    new_clinica = Clinica(nome=nome, email=email, senha=hashed_password)
    try:
        db.session.add(new_clinica)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao cadastrar la clínica: {e}")
        return False


@routes.route("/register-clinica", methods=["GET", "POST"])
def register_clinica():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        confirmar_senha = request.form.get("confirmar_senha")
        if senha != confirmar_senha:
            flash("As senhas não coincidem. Tente novamente.", "danger")
            return redirect(url_for("routes.register_clinica"))
        clinica_existente = Clinica.query.filter_by(email=email).first()
        if clinica_existente:
            flash("Este email já está registrado. Escolha outro.", "danger")
            return redirect(url_for("routes.register_clinica"))
        if create_clinica(nome, email, senha):
            flash("Cadastro da clínica realizado com sucesso!", "success")
            return redirect(url_for("routes.login"))
        else:
            flash("Erro ao cadastrar a clínica. Tente novamente mais tarde.", "danger")
    return render_template("registerClinica.html")


@routes.route("/register-pet", methods=["GET", "POST"])
def register_pet():
    user_id = session.get("user_id")
    if not user_id:
        flash("Você precisa estar logado para registrar um PET.", "warning")
        return redirect(url_for("routes.login"))
    if request.method == "POST":
        nome = request.form.get("nome")
        idade = request.form.get("idade")
        peso = request.form.get("peso")
        tipo = request.form.get("tipo")
        raca_genero = request.form.get("raca_genero")
        if not nome or not idade or not peso or not tipo or not raca_genero:
            flash("Todos os campos são obrigatórios. Por favor, preencha todos.", "danger")
            return redirect(url_for("routes.register_pet"))
        new_pet = Pet(
            nome=nome, idade=idade, peso=peso, tipo=tipo, raca_genero=raca_genero, user_id=user_id
        )
        if save_to_db(new_pet):
            # Após registrar um pet, o usuário vai para a página de confirmação/listagem de pets.
            return redirect(url_for("routes.confirmation_pet"))
    return render_template("registerPETT.html")


@routes.route("/confirmation-pet", methods=["GET"])
def confirmation_pet():
    user_id = session.get("user_id")
    if not user_id:
        flash("Acesso negado. Faça login para continuar.", "danger")
        return redirect(url_for("routes.login"))
    pets = Pet.query.filter_by(user_id=user_id).all()
    # A página confirmationPetInfo.html já tem um botão "Voltar para Protocolo", que é mais adequado que "Voltar para Initial"
    # Se não tem pets, o template confirmationPetInfo.html não será renderizado, o usuário será redirecionado para register_pet
    if not pets:
        flash("Você ainda não tem nenhum PET cadastrado. Que tal adicionar um agora?", "info")
        return redirect(url_for("routes.register_pet"))
    return render_template("confirmationPetInfo.html", pets=pets)


@routes.route("/delete-pet/<int:pet_id>", methods=["POST"])
def delete_pet(pet_id):
    user_id = session.get("user_id")
    if not user_id:
        flash("Acesso negado.", "danger")
        return redirect(url_for("routes.login"))
    pet = Pet.query.get(pet_id)
    if pet and pet.user_id == user_id:
        Vacina.query.filter_by(pet_id=pet_id).delete()
        Tratamento.query.filter_by(pet_id=pet_id).delete()
        Vermifugo.query.filter_by(pet_id=pet_id).delete()
        Exame.query.filter_by(pet_id=pet_id).delete()
        db.session.delete(pet)
        db.session.commit()
        flash("Pet e todos os seus registros de protocolo foram excluídos com sucesso!", "success")
    else:
        flash("Acesso negado ou pet não encontrado.", "danger")
    return redirect(url_for("routes.confirmation_pet"))


# Rota /initial restaurada para renderizar initial.html
@routes.route("/initial")
def initial():
    user_id = session.get("user_id")
    if not user_id:
        flash("Você precisa estar logado para acessar esta página.", "warning")
        return redirect(url_for("routes.login"))
    # Simplesmente renderiza a página initial.html se o usuário estiver logado.
    # A página initial.html já tem links para /confirmation-pet e /protocolo.
    return render_template("initial.html")


@routes.route("/protocolo", methods=["GET"])
@routes.route("/protocolo/<int:active_pet_id>", methods=["GET"])
def protocolo(active_pet_id=None):
    user_id = session.get("user_id")
    if not user_id:
        flash("Você precisa estar logado para acessar o protocolo.", "warning")
        return redirect(url_for("routes.login"))

    user = User.query.get(user_id)
    pets = user.pets if user else []

    selected_pet = None
    vacinas = []
    tratamentos = []
    vermifugos = []
    exames = []

    if active_pet_id:
        selected_pet = Pet.query.filter_by(id=active_pet_id, user_id=user_id).first()
        if not selected_pet:
            flash("Pet selecionado inválido ou não pertence a você.", "warning")
            active_pet_id = None
    elif pets:
        selected_pet = pets[0]
        active_pet_id = selected_pet.id

    if selected_pet:
        vacinas = Vacina.query.filter_by(pet_id=selected_pet.id, user_id=user_id).all()
        tratamentos = Tratamento.query.filter_by(pet_id=selected_pet.id, user_id=user_id).all()
        vermifugos = Vermifugo.query.filter_by(pet_id=selected_pet.id, user_id=user_id).all()
        exames = Exame.query.filter_by(pet_id=selected_pet.id, user_id=user_id).all()

    return render_template("protocolo.html",
                           pets=pets,
                           selected_pet=selected_pet,
                           active_pet_id=active_pet_id,
                           vacinas=vacinas,
                           tratamentos=tratamentos,
                           vermifugos=vermifugos,
                           exames=exames)


@routes.route("/get_protocolo_data/<int:pet_id>", methods=["GET"])
def get_protocolo_data(pet_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    pet = Pet.query.filter_by(id=pet_id, user_id=user_id).first()
    if not pet:
        return jsonify({"error": "Pet not found or access denied"}), 404

    vacinas_data = [{
        'nome_vacina': v.nome_vacina,
        'data_aplicacao': v.data_aplicacao.strftime('%Y-%m-%d') if v.data_aplicacao else None,
        'proxima_dose': v.proxima_dose.strftime('%Y-%m-%d') if v.proxima_dose else None,
        'status': v.status
    } for v in Vacina.query.filter_by(pet_id=pet_id, user_id=user_id).all()]
    tratamentos_data = [{
        'nome_tratamento': t.nome_tratamento,
        'data_inicio': t.data_inicio.strftime('%Y-%m-%d') if t.data_inicio else None,
        'data_conclusao': t.data_conclusao.strftime('%Y-%m-%d') if t.data_conclusao else None,
        'status': t.status
    } for t in Tratamento.query.filter_by(pet_id=pet_id, user_id=user_id).all()]
    vermifugos_data = [{
        'nome_vermifugo': ve.nome_vermifugo,
        'data_aplicacao': ve.data_aplicacao.strftime('%Y-%m-%d') if ve.data_aplicacao else None,
        'proxima_dose': ve.proxima_dose.strftime('%Y-%m-%d') if ve.proxima_dose else None,
        'status': ve.status
    } for ve in Vermifugo.query.filter_by(pet_id=pet_id, user_id=user_id).all()]
    exames_data = [{
        'tipo_exame': e.tipo_exame,
        'data_exame': e.data_exame.strftime('%Y-%m-%d') if e.data_exame else None,
        'resultado': e.resultado,
        'observacoes': e.observacoes
    } for e in Exame.query.filter_by(pet_id=pet_id, user_id=user_id).all()]

    return jsonify({
        "vacinas": vacinas_data,
        "tratamentos": tratamentos_data,
        "vermifugos": vermifugos_data,
        "exames": exames_data
    })


def parse_date(date_str):
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


@routes.route("/protocolo/adicionar_vacina/<int:pet_id>", methods=["POST"])
def adicionar_vacina(pet_id):
    user_id = session.get("user_id")
    if not user_id:
        flash("Acesso negado.", "danger")
        return redirect(url_for("routes.login"))

    pet = Pet.query.filter_by(id=pet_id, user_id=user_id).first()
    if not pet:
        flash("Pet não encontrado ou acesso negado.", "danger")
        return redirect(url_for("routes.protocolo"))

    if request.method == "POST":
        nome_vacina = request.form.get("nome_vacina")
        data_aplicacao_str = request.form.get("data_aplicacao")
        proxima_dose_str = request.form.get("proxima_dose")
        status = request.form.get("status_vacina")
        data_aplicacao = parse_date(data_aplicacao_str)
        proxima_dose = parse_date(proxima_dose_str)

        if not nome_vacina or not data_aplicacao or not status:
            flash("Nome da vacina, data de aplicação e status são obrigatórios.", "danger")
            return redirect(url_for("routes.protocolo", active_pet_id=pet_id))

        nova_vacina = Vacina(nome_vacina=nome_vacina, data_aplicacao=data_aplicacao, proxima_dose=proxima_dose,
                             status=status, pet_id=pet_id, user_id=user_id)
        if save_to_db(nova_vacina):
            flash("Vacina adicionada com sucesso!", "success")
        else:
            flash("Erro ao adicionar vacina.", "danger")
        return redirect(url_for("routes.protocolo", active_pet_id=pet_id))


@routes.route("/protocolo/adicionar_tratamento/<int:pet_id>", methods=["POST"])
def adicionar_tratamento(pet_id):
    user_id = session.get("user_id")
    if not user_id:
        flash("Acesso negado.", "danger")
        return redirect(url_for("routes.login"))

    pet = Pet.query.filter_by(id=pet_id, user_id=user_id).first()
    if not pet:
        flash("Pet não encontrado ou acesso negado.", "danger")
        return redirect(url_for("routes.protocolo"))

    if request.method == "POST":
        nome_tratamento = request.form.get("nome_tratamento")
        data_inicio_str = request.form.get("data_inicio")
        data_conclusao_str = request.form.get("data_conclusao")
        status = request.form.get("status_tratamento")
        data_inicio = parse_date(data_inicio_str)
        data_conclusao = parse_date(data_conclusao_str)

        if not nome_tratamento or not data_inicio or not status:
            flash("Nome do tratamento, data de início e status são obrigatórios.", "danger")
            return redirect(url_for("routes.protocolo", active_pet_id=pet_id))

        novo_tratamento = Tratamento(nome_tratamento=nome_tratamento, data_inicio=data_inicio,
                                     data_conclusao=data_conclusao, status=status, pet_id=pet_id, user_id=user_id)
        if save_to_db(novo_tratamento):
            flash("Tratamento adicionado com sucesso!", "success")
        else:
            flash("Erro ao adicionar tratamento.", "danger")
        return redirect(url_for("routes.protocolo", active_pet_id=pet_id))


@routes.route("/protocolo/adicionar_vermifugo/<int:pet_id>", methods=["POST"])
def adicionar_vermifugo(pet_id):
    user_id = session.get("user_id")
    if not user_id:
        flash("Acesso negado.", "danger")
        return redirect(url_for("routes.login"))

    pet = Pet.query.filter_by(id=pet_id, user_id=user_id).first()
    if not pet:
        flash("Pet não encontrado ou acesso negado.", "danger")
        return redirect(url_for("routes.protocolo"))

    if request.method == "POST":
        nome_vermifugo = request.form.get("nome_vermifugo")
        data_aplicacao_str = request.form.get("data_aplicacao_vermifugo")
        proxima_dose_str = request.form.get("proxima_dose_vermifugo")
        status = request.form.get("status_vermifugo")
        data_aplicacao = parse_date(data_aplicacao_str)
        proxima_dose = parse_date(proxima_dose_str)

        if not nome_vermifugo or not data_aplicacao or not status:
            flash("Nome do vermífugo, data de aplicação e status são obrigatórios.", "danger")
            return redirect(url_for("routes.protocolo", active_pet_id=pet_id))

        novo_vermifugo = Vermifugo(nome_vermifugo=nome_vermifugo, data_aplicacao=data_aplicacao,
                                   proxima_dose=proxima_dose, status=status, pet_id=pet_id, user_id=user_id)
        if save_to_db(novo_vermifugo):
            flash("Vermífugo adicionado com sucesso!", "success")
        else:
            flash("Erro ao adicionar vermífugo.", "danger")
        return redirect(url_for("routes.protocolo", active_pet_id=pet_id))


@routes.route("/protocolo/adicionar_exame/<int:pet_id>", methods=["POST"])
def adicionar_exame(pet_id):
    user_id = session.get("user_id")
    if not user_id:
        flash("Acesso negado.", "danger")
        return redirect(url_for("routes.login"))

    pet = Pet.query.filter_by(id=pet_id, user_id=user_id).first()
    if not pet:
        flash("Pet não encontrado ou acesso negado.", "danger")
        return redirect(url_for("routes.protocolo"))

    if request.method == "POST":
        tipo_exame = request.form.get("tipo_exame")
        data_exame_str = request.form.get("data_exame")
        resultado = request.form.get("resultado_exame")
        observacoes = request.form.get("observacoes_exame")
        data_exame = parse_date(data_exame_str)

        if not tipo_exame or not data_exame:
            flash("Tipo de exame e data do exame são obrigatórios.", "danger")
            return redirect(url_for("routes.protocolo", active_pet_id=pet_id))

        novo_exame = Exame(tipo_exame=tipo_exame, data_exame=data_exame, resultado=resultado, observacoes=observacoes,
                           pet_id=pet_id, user_id=user_id)
        if save_to_db(novo_exame):
            flash("Exame adicionado com sucesso!", "success")
        else:
            flash("Erro ao adicionar exame.", "danger")
        return redirect(url_for("routes.protocolo", active_pet_id=pet_id))


@routes.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Você foi desconectado.", "info")
    return redirect(url_for("routes.login"))

