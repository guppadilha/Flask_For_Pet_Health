import pytest
from website.models import User, Pet
from werkzeug.security import generate_password_hash

@pytest.fixture
def auth_user(app):
    """Fixture para criar um usuário de teste no banco de dados"""
    with app.app_context():
        user = User(
            usuario='testuser',
            email='test@example.com',
            senha=generate_password_hash('password123')
        )
        from website import db
        db.session.add(user)
        db.session.commit()
        return user

def test_login_post(client):
    """Teste básico para a rota de login (POST) com credenciais inválidas"""
    response = client.post('/login', data={
        'email': 'nonexistent@example.com',
        'senha': 'wrongpassword'
    })
    assert response.status_code == 200  # Retorna a página de login novamente

def test_register_post_password_mismatch(client):
    """Teste básico para a rota de registro (POST) com senhas que não coincidem"""
    response = client.post('/register', data={
        'usuario': 'newuser',
        'email': 'new@example.com',
        'senha': 'password123',
        'confirmar_senha': 'different123'
    }, follow_redirects=True)
    assert response.status_code == 200
    
def test_register_pet_redirect_when_not_logged_in(client):
    """Teste para verificar se a rota /register-pet redireciona quando não logado"""
    response = client.get('/register-pet')
    assert response.status_code == 302  # Redirecionamento
    assert '/login' in response.location

def test_confirmation_pet_redirect_when_not_logged_in(client):
    """Teste para verificar se a rota /confirmation-pet redireciona quando não logado"""
    response = client.get('/confirmation-pet')
    assert response.status_code == 302  # Redirecionamento
    assert '/login' in response.location
