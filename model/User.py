from flask_login import UserMixin
class User(UserMixin):
	def __init__(self, uid, username, encoding):
		self.uid = uid
		self.username = username
		self.encoding = encoding

	def get_id(self):
		return str(self.uid)