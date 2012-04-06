from ucsvlog.ReaderDB import ReaderDB
import sqlite3

class ReaderSqlite(ReaderDB):

    def db_get_connection(self,db):
        return sqlite3.connect(db)

    def db_create_table(self,table):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS "%s" (
                "id" INTEGER PRIMARY KEY,
                "parent" INTEGER,
                "file" TEXT
            );
        '''% table)

    def db_get_cols_count(self,table):
        self.cursor.execute('select * from "%s" limit 1' % self.table)
        return len(self.cursor.description)
        
    def db_alter_add_data_column(self,col_name):
        self.cursor.execute('''
            ALTER TABLE  "%s" ADD COLUMN "%s" TEXT
        '''% (self.table,col_name))

    def db_insert_row(self,data):
        self.cursor.execute('insert into "'+self.table+'" values ('+','.join(['?']*self.cols_count)+')',data)

    def import_all(self):
        super(ReaderSqlite,self).import_all()
        self.conn.commit()
