from flask import Flask
from flask import send_file

from .views.frontend import frontend_views
from .views.auth import oauth_views
from .views.auth import oauth
from .models import db as main_db
from .admin import register_admin


def create_app(config=None):
    app = Flask(
        __name__,
        template_folder='templates'
    )

    if isinstance(config, dict):
        app.config.update(config)
    elif config:
        app.config.from_pyfile(config)

    #: prepare for database
    main_db.init_app(app)
    main_db.app = app
    main_db.create_all()

    register_jinja(app)
    register_static(app)
    register_oauth(app, oauth)
    register_routes(app)
    register_admin(app, main_db)

    return app


def register_routes(app):
    app.register_blueprint(frontend_views)
    app.register_blueprint(oauth_views)
    return app


def register_oauth(app, oauth):
    app.config['GITHUB'].update(dict(
        request_token_params={'scope': 'user:email'},
        base_url='https://api.github.com/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize')
    )
    oauth.init_app(app)


def register_static(app):
    @app.route('/<file_name>.txt')
    def plain_file(file_name):
        return send_file(file_name)
    return app


def register_jinja(app):
    app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
    return app
