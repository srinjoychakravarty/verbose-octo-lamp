# /tests/test_user_model

import unittest
from src.app import db
from src.models import UserModel
# from project.tests.base import BaseTestCase


# class TestUserModel(BaseTestCase):
#
#     def test_encode_auth_token(self):
#         user = UserModel(
#             email='test@test.com',
#             password='test'
#         )
#         db.session.add(user)
#         db.session.commit()
#         auth_token = user.encode_auth_token(user.id)
        # self.assertTrue(isinstance(auth_token, bytes))

if __name__ == '__main__':
    unittest.main()
