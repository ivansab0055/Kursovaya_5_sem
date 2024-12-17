from app import KallosusNNApplication

app = KallosusNNApplication().create_app()

if __name__ == '__main__':
    # Если использовать `use_reloader=True`, сервер перезагружается дважды
    # Запускается только во время тестов, в docker будет запускаться app
    app.run(port=5001, debug=app.config['DEBUG'], use_reloader=True)
