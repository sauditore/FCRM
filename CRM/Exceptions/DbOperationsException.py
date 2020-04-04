__author__ = 'saeed'


class DBInsertException(Exception):
    def __init__(self, message):
        if message is not None:
            self.message = 'An error raised when inserting new data to DB : '+message
        else:
            self.message = 'Unknown error when trued to insert to DB'

    def __unicode__(self):
        return self.message


class DBSelectException(Exception):
    def __init__(self, message):
        if message is not None:
            self.message = 'An error raised when selecting data from DB : '+message
        else:
            self.message = 'Unknown error when selecting database records'

    def __unicode__(self):
        return self.message


class DBUpdateException(Exception):
    def __init__(self, message):
        if message is not None:
            self.message = 'An Error raised when updating the db : '+message
        else:
            self.message = 'Unknown error when updating database!'

    def __unicode__(self):
        return self.message

class DBRecordExist(Exception):
    def __init__(self, message):
        if message is not None:
            self.message = 'There is a record with same identity : '+message
        else :
            self.message = 'There is a record with same identity but i do not know where!'

    def __unicode__(self):
        return self.message