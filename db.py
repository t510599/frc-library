import pymysql as sql
from model.User import User
from datetime import datetime

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

    def query_book(self, book_id):
        command = 'SELECT * FROM `frc_library`.`books` WHERE `book_id` = %d'
        db = sql.connect(self.host, self.user, self.password, self.name)
        cursor = db.cursor()
        cursor.execute(command, book_id)
        result = cursor.fetchone()
        cursor.close()
        db.close()
        if result:
            if len(result) > 3:
                return Book(result[0], result[1], bool(result[2]), result[3], result[4])
            else:
                return Book(result[0], result[1], bool(result[2]))
        else:
            return None

    def borrow_book(self, book_ids, uid):
        lent_command = 'UPDATE `frc_library`.`books` SET `lent` = 1 WHERE `bookd_id` = %s'
        borrower_command = 'UPDATE `frc_library`.`books` SET `borrower_id` = %s WHERE `book_id` = %s'
        time_command = 'UPDATE `frc_library`.`books` SET `time` = {} WHERE `book_id` = %s'
        db = sql.connect(self.host, self.user, self.password, self.name)
        cursor = db.cursor()
        for book_id in book_ids:
            r1 = cursor.execute(lent_command, str(book_id))
            r2 = cursor.execute(borrower_command, str(uid), str(book_id))
            r3 = cursor.execute(time_command.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), str(book_id))
            db.commit()
            if r1 != 1 or r2 != 1 or r3 != 1:
                db.rollback()
                cursor.close()
                db.close()
                return False
        cursor.close()
        db.close()
        return True

    def return_book(self, book_ids):
        lent_command = 'UPDATE `frc_library``books` SET `lent` = 0 WHERE `book_id` = %s'
        borrower_command = 'UPDATE `frc_library`.`books` SET `borrower_id` = NULL WHERE `book_id` = %s'
        time_command = 'UPDATE `frc_library`.`books` SET `time` = NULL WHERE `book_id` = %s'
        db = sql.connect(self.host, self.user, self.password, self.name)
        cursor = db.cursor()
        for book_id in book_ids:
            r1 = cursor.execute(lent_command, str(book_id))
            r2 = cursor.execute(borrower_command, str(book_id))
            r3 = cursor.execute(time_command, str(book_id))
            db,commit()
            if r1 != 1 or r2 != 1 or r3 != 1:
                db.rollback()
                cursor.close()
                db.close()
                return False
        cursor.close()
        db.close()
        return True