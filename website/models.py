from . import db
from sqlalchemy.sql import func # Import func for default timestamps

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(150), nullable=False)
    failed_attempts = db.Column(db.Integer, default=0)

    clinica_id = db.Column(db.Integer, db.ForeignKey('clinica.id'), nullable=True)

    # Relacionamento explícito
    pets = db.relationship('Pet', backref='owner', lazy=True, order_by="Pet.id") # Added backref='owner'
    vacinas = db.relationship('Vacina', backref='user', lazy=True)
    tratamentos = db.relationship('Tratamento', backref='user', lazy=True)
    vermifugos = db.relationship('Vermifugo', backref='user', lazy=True)
    exames = db.relationship('Exame', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.usuario}>'


class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    peso = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    raca_genero = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relações explícitas
    # user = db.relationship('User') # Esta linha é redundante devido ao backref em User.pets
    vacinas = db.relationship('Vacina', backref='pet', lazy=True)
    tratamentos = db.relationship('Tratamento', backref='pet', lazy=True)
    vermifugos = db.relationship('Vermifugo', backref='pet', lazy=True)
    exames = db.relationship('Exame', backref='pet', lazy=True)


# Modelo Clinica
class Clinica(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(150), nullable=False)

    # Relacionamento com o modelo User
    usuarios = db.relationship('User', backref='clinica', lazy=True)

    def __repr__(self):
        return f"<Clinica {self.nome}>"


# Novas tabelas para informações do Pet

class Vacina(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_vacina = db.Column(db.String(100), nullable=False)
    data_aplicacao = db.Column(db.Date, nullable=False)
    proxima_dose = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), nullable=False)  # Ex: "Em Dia", "Atrasado"
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Adicionado user_id

    def __repr__(self):
        return f"<Vacina {self.nome_vacina} - Pet {self.pet_id} - User {self.user_id}>"


class Tratamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_tratamento = db.Column(db.String(150), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_conclusao = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), nullable=False)  # Ex: "Concluído", "Em Andamento", "Não Iniciado"
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Adicionado user_id

    def __repr__(self):
        return f"<Tratamento {self.nome_tratamento} - Pet {self.pet_id} - User {self.user_id}>"


class Vermifugo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_vermifugo = db.Column(db.String(100), nullable=False)
    data_aplicacao = db.Column(db.Date, nullable=False)
    proxima_dose = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), nullable=False)  # Ex: "Em Dia", "Atrasado"
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Adicionado user_id

    def __repr__(self):
        return f"<Vermifugo {self.nome_vermifugo} - Pet {self.pet_id} - User {self.user_id}>"


class Exame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo_exame = db.Column(db.String(100), nullable=False)
    data_exame = db.Column(db.Date, nullable=False)
    resultado = db.Column(db.Text, nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Adicionado user_id

    def __repr__(self):
        return f"<Exame {self.tipo_exame} - Pet {self.pet_id} - User {self.user_id}>"

