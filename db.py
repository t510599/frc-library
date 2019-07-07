import pymysql as sql

class UsernameTooLongError(Exception):
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

    def _check_user_exists(self, user_id, cursor):
        command = 'SELECT * FROM `frc_library`.`user` WHERE `user_id` = %s;'
        cursor.execute(command, user_id)
        result = cursor.fetchone()
        if result:
            return True
        else:
            return False
            
    #note: encoding here must be a str
    def create_user(self, username, encoding):
        if type(username) != str or encoding != str:
            raise TypeError('both username and encoding are str')
        if len(username) > 16:
            raise UsernameTooLongError('username should not exceed 16 characters')
        db = sql.connect(self.host, self.username, self.encodings, self.name)
        cursor = db.cursor()
        user_id = self._get_user_count(cursor) + 1
        command = 'INSERT INTO `frc_library`.`user` (`username`, `user_id`, `encoding`) VALUES (%s, %d, %s);'
        line = cursor.execute(command, username, user_id, encoding)
        db.commit()
        return self._check_user_exists(user_id, cursor)
        cursor.close()
        db.close()

    def 
