# src/models/UserModel.py

from marshmallow import fields, Schema
import datetime
from . import db, bcrypt
from .BlogpostModel import BlogpostSchema
from uuid import uuid4
# import sqlalchemy
# from sqlalchemy.dialects.postgresql import UUID

class UserModel(db.Model):
  """
  User Model
  """
  __tablename__ = 'users'
  # id = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid4)
  # id = db.Column(UUID(as_uuid = True), primary_key=True, server_default = sqlalchemy.text("uuid_generate_v4()"))
  id = db.Column(db.String(128), primary_key = True, default = uuid4)
  first_name = db.Column(db.String(128), nullable = False)
  last_name = db.Column(db.String(128), nullable = False)
  email_address = db.Column(db.String(128), unique = True, nullable = False)
  password = db.Column(db.String(128), nullable = True)
  account_created = db.Column(db.DateTime)
  account_updated = db.Column(db.DateTime)

  # class constructor
  def __init__(self, data):
    """
    Class constructor
    """
    self.first_name = data.get('first_name')
    self.last_name = data.get('last_name')
    self.email_address = data.get('email_address')
    self.password = self.__generate_hash(data.get('password')) # add this line
    self.account_created = datetime.datetime.utcnow()
    self.account_updated = datetime.datetime.utcnow()

  def save(self):
    db.session.add(self)
    db.session.commit()

  # add this new method
  def __generate_hash(self, password):
    return bcrypt.generate_password_hash(password, rounds=10).decode("utf-8")

  # add this new method
  def check_hash(self, password):
    return bcrypt.check_password_hash(self.password, password)

  def update(self, data):
    for key, item in data.items():
      if key == 'password': # add this new line
        self.password = self.__generate_hash(value) # add this new line
      setattr(self, key, item)
    self.modified_at = datetime.datetime.utcnow()
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  @staticmethod
  def get_all_users():
    return UserModel.query.all()

  @staticmethod
  def get_one_user(id):
    return UserModel.query.get(id)

  def __repr(self):
    return '<id {}>'.format(self.id)

# add this class
class UserSchema(Schema):
  id = fields.Str(dump_only = True)
  first_name = fields.Str(required = True)
  last_name = fields.Str(required = True)
  email_address = fields.Email(required = True)
  password = fields.Str(required = True, load_only = True)
  account_created = fields.DateTime(dump_only = True)
  account_updated = fields.DateTime(dump_only = True)
