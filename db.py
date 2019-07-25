import pymysql as sql
from model.User import User
from model.Book import Book
from datetime import datetime
import numpy as np

class UsernameTooLongError(Exception):
    pass
class UsernameAlreadyExistsError(Exception):
    pass

class LibraryDb:
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password
        self.name = 'frc_library'

    def _get_user_count(self, cursor):
        command = 'SELECT COUNT(`user_id`) FROM `frc_library`.`user`;'
        cursor.execute(command)
        result = cursor.fetchone()
        return result[0]

    def _get_user(self, user_id, cursor):
        command = 'SELECT * FROM `frc_library`.`user` WHERE `user_id` = %s;'
        cursor.execute(command, user_id)
        result = cursor.fetchone()
        if result:
            return User(user_id, result[0], result[2])
        else:
            return None

    #note: encoding here must be a str
    def create_user(self, username, encoding):
        if type(username) != str:
            raise TypeError('username must be a str')
        if len(username) > 16:
            raise UsernameTooLongError('username should not exceed 16 characters')
        db = sql.connect(self.host, self.user, self.password, self.name)
        cursor = db.cursor()
        user_id = self._get_user_count(cursor) + 1
        command = 'INSERT INTO `frc_library`.`user` (`username`, `user_id`, `encoding`) VALUES (%s, %s, %s);'
        try:
            cursor.execute(command, (username, user_id, encoding))
            db.commit()
        except sql.IntegrityError:
            print('error occur, rollback')
            db.rollback()
            raise UsernameAlreadyExistsError('username already exists')
        except Exception as e:
            print('unknown err', e)
        finally:
            user = self._get_user(user_id, cursor)
            cursor.close()
            db.close()
            return user
        

    def query_user(self, username):
        command = 'SELECT * FROM `frc_library`.`user` WHERE `username` = %s'
        db = sql.connect(self.host, self.user, self.password, self.name)
        cursor = db.cursor()
        cursor.execute(command, username)
        result = cursor.fetchone()
        cursor.close()
        db.close()
        if result:
            return User(result[1], username, result[2])
        else:
            return None

    def get_user(self, uid):
        db = sql.connect(self.host, self.user, self.password, self.name)
        cursor = db.cursor()
        return self._get_user(uid, cursor)

    def query_user_encodings(self):
        db = sql.connect(self.host, self.user, self.password, self.name)
        cursor = db.cursor()
        command = 'SELECT `username`, `encoding` FROM `frc_library`.`user`;'
        cursor.execute(command)
        results = cursor.fetchall()
        encodings = dict()
        for result in results:
            encodings[result[0]] = np.fromstring(result[1], dtype=np.float64)
        return encodings

    def query_book(self, book_id):
        command = 'SELECT * FROM `frc_library`.`books` WHERE `book_id` = %s;'
        db = sql.connect(self.host, self.user, self.password, self.name)
        cursor = db.cursor()
        cursor.execute(command, book_id)
        result = cursor.fetchone()
        cursor.close()
        db.close()
        if result:
            return Book(result[0], result[1], bool(result[2]), result[3], result[4])
        else:
            return None

    def borrow_book(self, book_ids, current_user):
        lent_command = 'UPDATE `frc_library`.`books` SET `lent` = 1, `borrower_id` = %s, `time` = %s WHERE `book_id` = %s AND `lent` = 0;'
        db = sql.connect(self.host, self.user, self.password, self.name)
        cursor = db.cursor()
        uid = current_user.uid
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        results = []
        for book_id in book_ids:
            r1 = cursor.execute(lent_command, (uid, time, book_id))
            db.commit()
            if r1 != 1:
                db.rollback()
                results.append(False)
            else:
                results.append(True)
        cursor.close()
        db.close()
        return results

    def return_book(self, book_ids):
        lent_command = 'UPDATE `frc_library`.`books` SET `lent` = 0, `borrower_id` = NULL, `time` = NULL WHERE `book_id` = %s AND `lent` = 1;'
        db = sql.connect(self.host, self.user, self.password, self.name)
        cursor = db.cursor()
        results = []
        for book_id in book_ids:
            r1 = cursor.execute(lent_command, book_id)
            db.commit()
            if r1 != 1:
                db.rollback()
                results.append(False)
            else:
                results.append(True)
        cursor.close()
        db.close()
        return results

    def get_user_log(self, user_id):
        command = 'SELECT * FROM `frc_library`.`books` WHERE `borrower_id` = %s'
        db = sql.connect(self.host, self.user, self.password, self.name)
        cursor = db.cursor()
        cursor.execute(command, user_id)
        results = cursor.fetchall()
        books = []
        for result in results:
            books.append(Book(result[0], result[1], bool(result[2]), result[3], result[4]))
        return books