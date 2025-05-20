import pytest

def test_welcome_route(client):
    """Teste básico para a rota de boas-vindas '/'"""
    response = client.get('/')
    assert response.status_code == 200
    
def test_login_route_get(client):
    """Teste básico para a rota de login (GET)"""
    response = client.get('/login')
    assert response.status_code == 200
    
def test_register_route_get(client):
    """Teste básico para a rota de registro (GET)"""
    response = client.get('/register')
    assert response.status_code == 200
    
def test_register_clinica_route_get(client):
    """Teste básico para a rota de registro de clínica (GET)"""
    response = client.get('/register-clinica')
    assert response.status_code == 200
    
def test_initial_route_redirect(client):
    """Teste para verificar se a rota /initial redireciona quando não logado"""
    response = client.get('/initial')
    assert response.status_code == 302  # Redirecionamento
    assert '/login' in response.location
    
def test_protocolo_route_redirect(client):
    """Teste para verificar se a rota /protocolo redireciona quando não logado"""
    response = client.get('/protocolo')
    assert response.status_code == 302  # Redirecionamento
    assert '/login' in response.location
