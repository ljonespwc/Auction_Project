from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config['SECRET KEY'] = 'jhg56tyrqwye098034zbnxcv7456'
    
    from .views import views
    from .auth import auth
    # add other blueprints here
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    # register other blueprints here
    
    return app