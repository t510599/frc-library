#lent should be a boolean
class Book:
	def __init__(self, book_id, name, lent, borrower = None, time = None):
		self.book_id = book_id
		self.name = name
		self.lent = lent
		self.borrower = borrower
		self.time = time