import unittest
from ucsvlog.Reader import Reader
from pprint import pprint
class UCSVReaderToPy(Reader):
    def __init__(self,*args,**kwargs):
        self.py_data = []
        self.py_wrong_lines = []
        super(UCSVReaderToPy,self).__init__(*args,**kwargs)
    def write_row(self,row):
        self.py_data.append(row)
        return row


class ReadsTests(unittest.TestCase):
    def test_simple_3_lines(self):
        r = UCSVReaderToPy('tests/log_files/001_simple_3_lines.ucsv')
        r.import_all()
        #self.assertEqual(r.py_wrong_lines,[])
        self.assertEqual(r.py_data,[
            [u'2010-12-24T21:59:20.471290',
            u'',
            u'3',
            u'__call__',
            u'/home/oduvan/www/python-ucsvlog/UCSVLog.py',
            u'70',
            u'log',
            u'ho'],

            [u'2010-12-24T21:59:20.472136',
            u'',
            u'3',
            u'__call__',
            u'/home/oduvan/www/python-ucsvlog/UCSVLog.py',
            u'70',
            u'log',
            u'hi'],

            [u'2010-12-24T21:59:20.472486',
            u'',
            u'3',
            u'__call__',
            u'/home/oduvan/www/python-ucsvlog/UCSVLog.py',
            u'70',
            u'log',
            u'g',
            u'p']
        ])
    
    def test_simple_3_lines_with_close(self):
        r = UCSVReaderToPy('tests/log_files/005_simple_3_lines_with_close.ucsv',close_row='.')
        r.import_all()
        #self.assertEqual(r.py_wrong_lines,[])
        self.assertEqual(r.py_data,[
            [u'2010-12-24T21:59:20.471290',
            u'',
            u'3',
            u'__call__',
            u'/home/oduvan/www/python-ucsvlog/UCSVLog.py',
            u'70',
            u'log',
            u'ho'],

            [u'2010-12-24T21:59:20.472136',
            u'',
            u'3',
            u'__call__',
            u'/home/oduvan/www/python-ucsvlog/UCSVLog.py',
            u'70',
            u'log',
            u'hi'],

            [u'2010-12-24T21:59:20.472486',
            u'',
            u'3',
            u'__call__',
            u'/home/oduvan/www/python-ucsvlog/UCSVLog.py',
            u'70',
            u'log',
            u'g',
            u'p']
        ])
        
    def test_simple_3_lines_with_close_one_fail(self):
        r = UCSVReaderToPy('tests/log_files/006_simple_3_lines_with_close_one_fail.ucsv',close_row='.')
        r.import_all()
        #self.assertEqual(r.py_wrong_lines,[])
        self.assertEqual(r.py_data,[
            [u'2010-12-24T21:59:20.471290',
            u'',
            u'3',
            u'__call__',
            u'/home/oduvan/www/python-ucsvlog/UCSVLog.py',
            u'70',
            u'log',
            u'ho'],
            [u'2010-12-24T21:59:20.472486',
            u'',
            u'3',
            u'__call__',
            u'/home/oduvan/www/python-ucsvlog/UCSVLog.py',
            u'70',
            u'log',
            u'g',
            u'p']
        ])
    
    def test_one_by_one(self):
        r = UCSVReaderToPy('tests/log_files/001_simple_3_lines.ucsv')
        r_iter = r.all_records()
        try: 
            self.assertEqual(r_iter.__next__(),
                             [u'2010-12-24T21:59:20.471290', u'', u'3', u'__call__', u'/home/oduvan/www/python-ucsvlog/UCSVLog.py', u'70', u'log', u'ho'])
            self.assertEqual(r_iter.__next__(),
                             [u'2010-12-24T21:59:20.472136', u'', u'3', u'__call__', u'/home/oduvan/www/python-ucsvlog/UCSVLog.py', u'70', u'log', u'hi'])
            self.assertEqual(r_iter.__next__(),
                             [u'2010-12-24T21:59:20.472486', u'', u'3', u'__call__', u'/home/oduvan/www/python-ucsvlog/UCSVLog.py', u'70', u'log', u'g', u'p'])
        except AttributeError:
            self.assertEqual(r_iter.next(),
                             [u'2010-12-24T21:59:20.471290', u'', u'3', u'__call__', u'/home/oduvan/www/python-ucsvlog/UCSVLog.py', u'70', u'log', u'ho'])
            self.assertEqual(r_iter.next(),
                             [u'2010-12-24T21:59:20.472136', u'', u'3', u'__call__', u'/home/oduvan/www/python-ucsvlog/UCSVLog.py', u'70', u'log', u'hi'])
            self.assertEqual(r_iter.next(),
                             [u'2010-12-24T21:59:20.472486', u'', u'3', u'__call__', u'/home/oduvan/www/python-ucsvlog/UCSVLog.py', u'70', u'log', u'g', u'p'])

        
                            
    def test_multiline_record(self):
        r = UCSVReaderToPy('tests/log_files/002_multyline_record.ucsv')
        r.import_all()
        self.assertEqual(r.py_data,[
            [u'70', u'log', u'ho'],
             [u'70', u'log', u'ho\n\nhi\n\n\ntest 3\n'],
             [u'70', u'lo\n5\n6\ng', u'ho']
            ])
    def test_with_spec_symbols(self):
        r = UCSVReaderToPy('tests/log_files/003_with_spec_symbols.ucsv')
        r.import_all()
        #import ipdb;ipdb.set_trace()
        self.assertEqual(r.py_data,[
            [u'70', u'log', u'ho'],
            [u'70', u'log', u'ho\n" quoted text "', u'I,m,t'],
            [u'"'],
            [u'""'],
            [u'",","",', u'simple text']
        ])

    def test_with_ru_unicode(self):
        r = UCSVReaderToPy('tests/log_files/004_with_ru_unicode.ucsv')
        r.import_all()
        [[u'70', u'log', u'ho'],
         [u'70',
          u'log',
          u'ho\n" quoted text "',
          u'I,m,ooio\n{% trans "\u0421\u043e\u0442\u0440\u0443\u0434\u043d\u0438\u043a\u0438"\n']
         ]

