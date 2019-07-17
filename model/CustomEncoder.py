from flask.json import JSONEncoder
from . import Book
from . import User
class CustomEncoder(JSONEncoder):
	def default(self, obj):
		if isinstance(obj, User):
			return {
				'uid': obj.uid,
				'username': obj.username,
				'encoding': obj.encoding
			}
		elif isinstance(obj, Book):
			return {
				'book_id': obj.book_id,
				'name': obj.name,
				'lent': obj.lent,
				'borrower': obj.borrower,
				'time': obj.time
			}
		else:
			return JSONEncoder.default(obj)