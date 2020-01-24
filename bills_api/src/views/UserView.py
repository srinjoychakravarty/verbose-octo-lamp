#/src/views/UserView

from flask import request, json, Response, Blueprint, g
from ..models.UserModel import UserModel, UserSchema
from ..shared.Authentication import Auth
import re, uuid

# from flask_httpauth import HTTPBasicAuth
# from werkzeug.security import generate_password_hash, check_password_hash
#
# auth = HTTPBasicAuth()

user_api = Blueprint('user_api', __name__)
user_schema = UserSchema()

@user_api.route('/', methods = ['POST'])
def create():
  """
  Create User Function
  """
  req_data = request.get_json()
  # data = user_schema.load(req_data)
  # Verify non-email username cannot be used for account creation
  valid_email = True
  email_error = ''
  attempted_email = req_data.get('email_address')
  if len(attempted_email) < 7:
    valid_email = False
    email_error = 'email shorter than 7 characters'
  elif re.match("^.+@(\[?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$", attempted_email) == None:
    valid_email = False
    email_error = 'please use a standard email convention'
  if valid_email:
      if UserModel.get_user_by_email(attempted_email):
        # check if user already exist in the db
        message = {'error': 'User already exist, please supply another email address'}
        return custom_response(message, 400)
      # Verify that weak passwords cannot be used to create account
      attempted_password = req_data.get('password')
      SpecialSym =['$', '@', '#', '%', '!', '^', '&', '*', '(', ')']
      password_error = ''
      valid_password = True
      if len(attempted_password) < 9:
          valid_password = False
          password_error = 'password shorter than 9 characters'
      elif not any(char.isdigit() for char in attempted_password):
          password_error = 'Password should have at least one numeral'
          valid_password = False
      elif not any(char.isupper() for char in attempted_password):
          password_error = 'Password should have at least one uppercase letter'
          valid_password = False
      elif not any(char.islower() for char in attempted_password):
          password_error = 'Password should have at least one lowercase letter'
          valid_password = False
      elif not any(char in SpecialSym for char in attempted_password):
          password_error = 'Password should have at least one of the symbols $ @ # % ! ^ & * ( )'
          valid_password = False
      if valid_password:
          new_uuid = uuid.uuid4()
          data = user_schema.load(req_data)
          data.update({'id': str(new_uuid)})
          user = UserModel(data)
          user.save()
          # change jwt token to basic authentication
          ser_data = user_schema.dump(user)
          # generate basic auth token and return as res below ???
          token = Auth.generate_token(ser_data.get('id'))
          return custom_response({'jwt_token': token}, 201)
      else:
          return custom_response({'error': password_error}, 400)
  else:
      return custom_response({'error': email_error}, 400)


# # add this new method
# @user_api.route('/all', methods = ['GET'])
# @Auth.auth_required
# def get_all():
#   """
#   Get all users
#   """
#   users = UserModel.get_all_users()
#   ser_users = user_schema.dump(users, many = True)
#   return custom_response(ser_users, 200)

# # user can get any other user via their id (might need to be removed)
# @user_api.route('/<int:user_id>', methods = ['GET'])
# @Auth.auth_required
# def get_a_user(user_id):
#   """
#   Get a single user
#   """
#   user = UserModel.get_one_user(user_id)
#   if not user:
#     return custom_response({'error': 'user not found'}, 404)
#   ser_user = user_schema.dump(user)
#   return custom_response(ser_user, 200)

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
