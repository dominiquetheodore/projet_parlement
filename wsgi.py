from app import app
app.secret_key = 'super_secret_key'

if __name__ == "__main__":
    app.config['SESSION_TYPE'] = 'filesystem'
    sess.init_app(app)
    app.run()
