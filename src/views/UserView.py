#/src/views/UserView

from flask import request, json, Response, Blueprint, g
from ..models.UserModel import UserModel, UserSchema
from ..shared.Authentication import Auth
import uuid

user_api = Blueprint('user_api', __name__)
user_schema = UserSchema()

@user_api.route('/', methods = ['POST'])
def create():
  """
  Create User Function
  """
  req_data = request.get_json()
  data = user_schema.load(req_data)
  # check if user already exist in the db
  if UserModel.get_user_by_email(data.get('email_address')):
    message = {'error': 'User already exist, please supply another email address'}
    return custom_response(message, 400)
  new_uuid = uuid.uuid4()
  data.update({'id': str(new_uuid)})
  user = UserModel(data)
  user.save()
  # change jwt token to basic authentication
  ser_data = user_schema.dump(user)
  # generate basic auth token and return as res below ???
  token = Auth.generate_token(ser_data.get('id'))
  return custom_response({'jwt_token': token}, 201)

# add this new method
@user_api.route('/', methods = ['GET'])
@Auth.auth_required
def get_all():
  """
  Get all users
  """
  users = UserModel.get_all_users()
  ser_users = user_schema.dump(users, many = True)
  return custom_response(ser_users, 200)

# user can get any other user via their id (might need to be removed)
@user_api.route('/<int:user_id>', methods = ['GET'])
@Auth.auth_required
def get_a_user(user_id):
  """
  Get a single user
  """
  user = UserModel.get_one_user(user_id)
  if not user:
    return custom_response({'error': 'user not found'}, 404)
  ser_user = user_schema.dump(user)
  return custom_response(ser_user, 200)

@user_api.route('/self', methods = ['GET'])
@Auth.auth_required
def get_self():
  """
  Get self
  """
  user = UserModel.get_one_user(g.user.get('id'))
  ser_user = user_schema.dump(user)
  return custom_response(ser_user, 200)

@user_api.route('/self', methods = ['PUT'])
@Auth.auth_required
def update():
  """
  Update self
  """
  req_data = request.get_json()
  update_attempt_list = list(req_data.keys())
  if ("account_updated" in update_attempt_list or "email_address" in update_attempt_list or "account_created" in update_attempt_list):
      return custom_response({'error': 'you cant update email address or tamper with timestamps'}, 400)
  else:
      data = user_schema.load(req_data, partial = True)
      user = UserModel.get_one_user(g.user.get('id'))
      user.update(data)
      ser_user = user_schema.dump(user)
      return custom_response(ser_user, 200)


@user_api.route('/self', methods = ['DELETE'])
@Auth.auth_required
def delete():
  """
  Delete a user
  """
  user = UserModel.get_one_user(g.user.get('id'))
  user.delete()
  return custom_response({'message': 'deleted'}, 204)

@user_api.route('/login', methods = ['POST'])
def login():
  """
  User Login Function
  """
  req_data = request.get_json()
  data = user_schema.load(req_data, partial = True)
  if not data.get('email_address') or not data.get('password'):
    return custom_response({'error': 'you need email and password to sign in'}, 400)
  user = UserModel.get_user_by_email(data.get('email_address'))
  if not user:
    return custom_response({'error': 'user does not exist for given email address'}, 400)
  if not user.check_hash(data.get('password')):
    return custom_response({'error': 'invalid credentials: password does not match'}, 400)
  ser_data = user_schema.dump(user)
  token = Auth.generate_token(ser_data.get('id'))
  return custom_response({'jwt_token': token}, 200)

def custom_response(res, status_code):
  """
  Custom Response Function
  """
  return Response(
    mimetype = "application/json",
    response = json.dumps(res),
    status = status_code
  )
