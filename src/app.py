#src/app.py

from flask import Flask
from .config import app_config
from .models import db, bcrypt

def create_app(env_name):
  """
  Create app
  """
  # app initiliazation
  app = Flask(__name__)

  app.config['SQLALCHEMY_ECHO'] = True                              # Configure the SQLAlchemy part of the app instance
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.config.from_object(app_config[env_name])
  bcrypt.init_app(app) # initializing bcrypt
  db.init_app(app) # add this line

  @app.route('/', methods=['GET'])
  def index():
    """
    example endpoint
    """
    return 'Congratulations! Your first endpoint is working!'

  return app
