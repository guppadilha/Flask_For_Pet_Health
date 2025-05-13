from website import create_app

app = create_app()

if __name__ == '__main__':
    # Inicializa o banco de dados (cria as tabelas se não existirem)
    with app.app_context():
        db.create_all() # db precisa ser importado de website ou website.models
    app.run(debug=True, host='0.0.0.0', port=5000)
