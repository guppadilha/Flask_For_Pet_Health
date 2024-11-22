from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(150), nullable=False)
    failed_attempts = db.Column(db.Integer, default=0)
    
    clinica_id = db.Column(db.Integer, db.ForeignKey('clinica.id'), nullable=True)

    # Relacionamento explícito
    pets = db.relationship('Pet', lazy=True, order_by="Pet.id")

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

    # Apenas esta relação explícita
    user = db.relationship('User')


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
