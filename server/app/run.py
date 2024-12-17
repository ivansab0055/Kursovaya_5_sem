from app import app

if __name__ == '__main__':
    # если `use_reloader=True`, сервер загружается дважды
    app.run(port=5000, debug=app.config['DEBUG'], use_reloader=True)
