from datetime import datetime
import time
from ucsvlog.Reader import Reader

SYS_LENGTH = 3
DATA_COL_PREFIX = 'd_'

class ReaderDB(Reader):
    def __init__(self,db,table,*args,**kwargs):
        self.db = db
        self.table = table
        self.conn = self.db_get_connection(db)
        self.cursor = self.db_get_cursor()
        self.db_create_table(table)
        self.cols_count = self.db_get_cols_count(table)
        super(ReaderDB,self).__init__(*args,**kwargs)

    def db_create_table(self,table):
        raise ImplementationError('Override  create table')

    def db_get_cols_count(self,table):
        raise ImplementationError('Override get cols count')

    def db_get_connection(self,db):
        raise ImplementationError('Override conect to db')

    def db_get_cursor(self):
        return self.conn.cursor()
        

    def db_alter_add_data_column(self,col_name):
        raise ImplementationError('Override alter table')

    def db_insert_row(data):
        raise ImplementationError('Override insert row')


    def add_cols(self,count):
        for i in range(1,count+1):
            self.db_alter_add_data_column(DATA_COL_PREFIX + str(i+self.cols_count - SYS_LENGTH))
        self.cols_count += count

    def parse_key(self,key):
        key_pieces = key.split(';')
        dt = datetime.strptime(key_pieces[0],'%Y-%m-%dT%H:%M:%S.%f')
        return int(time.mktime(dt.timetuple())) * 100000000 + dt.microsecond * 100 + int(key_pieces[1])


    def write_row(self,data):
        len_data = len(data) + 1
        if len_data > self.cols_count:
            self.add_cols(len_data - self.cols_count)
        elif len_data < self.cols_count:
            data = data + [None] * (self.cols_count-len_data)

        r_id = self.parse_key(data[0])
        r_parent = data[1] and self.parse_key(data[1]) or 0
        self.db_insert_row([r_id,r_parent,self.filename] + data[2:])
