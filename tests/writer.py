import unittest
from ucsvlog.Logger import Logger
import os
REL_FOLDER = os.path.dirname(os.path.dirname(__file__))

class MyFH(object):
    def __init__(self):
        self.data = ''
        self.last_read_position = 0
        
    def write(self,data):
        self.data += data
        
    def get_last_read(self):
        try:
            return self.data[self.last_read_position:]
        finally:
            self.last_read_position = len(self.data)
        
        

class EmptyLogger(Logger):
    index_counter = 0
    def _init_cur_fh(self):
        self._test = MyFH()
        return self._test
    def gen_record_key(self):
        self.index_counter += 1
        return self.index_counter

class TestLogger(unittest.TestCase):
    def assertStoredC(self,data):
        self.assertEqual(self.l._test.get_last_read(),data)




class TestEmptyLogger(TestLogger):
    def setUp(self):
        self.l = EmptyLogger('/var/log/django/{year}-{month}.ucsv',\
                              func_fields=['stacksize','fname','filename'],\
                              related_folder =REL_FOLDER )

    def test_simple_log(self):
        self.l.log('Oh')
        self.assertStoredC('''
"1,","0,"test_simple_log,"tests/writer.py,"log,"Oh''')
    
    def test_call_stack(self):
        def infunction():
            self.l.log('second')
            self.l.log('third', stack=1)
        self.l.log('first')
        infunction()
        self.assertStoredC('''
"1,","0,"test_call_stack,"tests/writer.py,"log,"first
"2,","0,"infunction,"tests/writer.py,"log,"second
"3,","1,"test_call_stack,"tests/writer.py,"log,"third''')

    def test_2simple_log(self):
        self.l.log('Oh')
        self.l.log('loh')
        self.assertStoredC('''
"1,","0,"test_2simple_log,"tests/writer.py,"log,"Oh
"2,","0,"test_2simple_log,"tests/writer.py,"log,"loh''')

    def test_different_names(self):
        self.l('oh')
        self.l.dbg('debug information')
        self.l.crt('critical information')
        self.assertStoredC('''
"1,","0,"test_different_names,"tests/writer.py,"log,"oh
"2,","0,"test_different_names,"tests/writer.py,"dbg,"debug information
"3,","0,"test_different_names,"tests/writer.py,"crt,"critical information''')
        
        

    def test_log_array(self):
        self.l(['first','second'])
        self.l.imp(['some','important','data'])
        self.l.trc(['some','trace',['many','of','my']])
        self.assertStoredC('''
"1,","0,"test_log_array,"tests/writer.py,"log,"first,"second
"2,","0,"test_log_array,"tests/writer.py,"imp,"some,"important,"data
"3,","0,"test_log_array,"tests/writer.py,"trc,"some,"trace,"['many', 'of', 'my']''')

    def test_single_append_log(self):
        self.l('Simple line')
        self.l.a_log('first','Open first node')
        self.l('First line inside "first"')
        self.l('Second line inside "first"')
        self.l.c_log('first','Close first node')
        self.l('Second Simple line')
        self.assertStoredC('''
"1,","0,"test_single_append_log,"tests/writer.py,"log,"Simple line
"2,","0,"test_single_append_log,"tests/writer.py,"a_log,"first,"Open first node
"3,"2,"0,"test_single_append_log,"tests/writer.py,"log,"First line inside ""first""
"4,"2,"0,"test_single_append_log,"tests/writer.py,"log,"Second line inside ""first""
"5,"2,"0,"test_single_append_log,"tests/writer.py,"c_log,"first,"Close first node
"6,","0,"test_single_append_log,"tests/writer.py,"log,"Second Simple line''')
        

    def test_single_append_two_close(self):
        self.l.a_log('first','Open first node')
        self.l('Second line inside "first"')
        self.l.c_log('first','Close first node')
        self.l.c_log('first','Close first again node')
        self.assertStoredC('''
"1,","0,"test_single_append_two_close,"tests/writer.py,"a_log,"first,"Open first node
"2,"1,"0,"test_single_append_two_close,"tests/writer.py,"log,"Second line inside ""first""
"3,"1,"0,"test_single_append_two_close,"tests/writer.py,"c_log,"first,"Close first node
"4,","0,"test_single_append_two_close,"tests/writer.py,"log,"first,"Close first again node''')




    def test_two_append_log(self):
        self.l('Simple line')
        self.l.a_log('first','Open first node')
        self.l('First line inside "first"')
        self.l('Second line inside "first"')
        self.l.a_log('second','Open second node')
        self.l('Single line inside "second"')
        self.l.c_log('second','Close second node')
        self.l('Third line inside "first"')
        self.l.c_log('first','Close first node')
        self.l('Second Simple line')
        self.assertStoredC('''
"1,","0,"test_two_append_log,"tests/writer.py,"log,"Simple line
"2,","0,"test_two_append_log,"tests/writer.py,"a_log,"first,"Open first node
"3,"2,"0,"test_two_append_log,"tests/writer.py,"log,"First line inside ""first""
"4,"2,"0,"test_two_append_log,"tests/writer.py,"log,"Second line inside ""first""
"5,"2,"0,"test_two_append_log,"tests/writer.py,"a_log,"second,"Open second node
"6,"5,"0,"test_two_append_log,"tests/writer.py,"log,"Single line inside ""second""
"7,"5,"0,"test_two_append_log,"tests/writer.py,"c_log,"second,"Close second node
"8,"2,"0,"test_two_append_log,"tests/writer.py,"log,"Third line inside ""first""
"9,"2,"0,"test_two_append_log,"tests/writer.py,"c_log,"first,"Close first node
"10,","0,"test_two_append_log,"tests/writer.py,"log,"Second Simple line''')


class TestEmptyProductLogger(TestLogger):
    def setUp(self):
        self.l = EmptyLogger('/var/log/django/{year}-{month}.ucsv',[
                'crt',
                'err',
                'imp',
                'inf',
                'log'
        ],func_fields=['stacksize','fname','filename'],\
          related_folder=REL_FOLDER)

    def test_show_not_all(self):
        self.l('Info')
        self.l.dbg('Not show')
        self.l.trc('Trace not show too')
        self.l.err('Some critical information')

        self.assertStoredC('''
"1,","0,"test_show_not_all,"tests/writer.py,"log,"Info
"2,","0,"test_show_not_all,"tests/writer.py,"err,"Some critical information''')

    def test_hide_parents(self):
        self.l('Simple line')
        self.l.a_dbg('first','Open first node')
        self.l('First line inside "first"')
        self.l('Second line inside "first"')
        self.l.c_dbg('first','Close first node')
        self.l('Second Simple line')

        self.l.a_log('second','Open second node')
        self.l('Single line inside "second"')
        self.l.c_log('second','Close second node')
        self.l('Third line inside "first"')
        self.assertStoredC('''
"1,","0,"test_hide_parents,"tests/writer.py,"log,"Simple line
"2,","0,"test_hide_parents,"tests/writer.py,"log,"First line inside ""first""
"3,","0,"test_hide_parents,"tests/writer.py,"log,"Second line inside ""first""
"4,","0,"test_hide_parents,"tests/writer.py,"log,"Second Simple line
"5,","0,"test_hide_parents,"tests/writer.py,"a_log,"second,"Open second node
"6,"5,"0,"test_hide_parents,"tests/writer.py,"log,"Single line inside ""second""
"7,"5,"0,"test_hide_parents,"tests/writer.py,"c_log,"second,"Close second node
"8,","0,"test_hide_parents,"tests/writer.py,"log,"Third line inside ""first""''')

    def test_two_hide_parents(self):
        self.l('Simple line')
        self.l.a_log('first','Open first node')
        self.l.a_trc('second','Open first node')
        self.l('First line inside "first"')
        self.l.c_trc('second','Close first node')
        self.l('Second line inside "first"')
        self.l.c_log('first','Close first node')
        self.l('Second Simple line')
        self.assertStoredC('''
"1,","0,"test_two_hide_parents,"tests/writer.py,"log,"Simple line
"2,","0,"test_two_hide_parents,"tests/writer.py,"a_log,"first,"Open first node
"3,"2,"0,"test_two_hide_parents,"tests/writer.py,"log,"First line inside ""first""
"4,"2,"0,"test_two_hide_parents,"tests/writer.py,"log,"Second line inside ""first""
"5,"2,"0,"test_two_hide_parents,"tests/writer.py,"c_log,"first,"Close first node
"6,","0,"test_two_hide_parents,"tests/writer.py,"log,"Second Simple line''')

    def test_two_hide2_parents(self):
        self.l('Simple line')
        self.l.a_trc('first','Open first node')
        self.l.a_log('second','Open first node')
        self.l('First line inside "first"')
        self.l.c_log('second','Close first node')
        self.l('Second line inside "first"')
        self.l.c_trc('first','Close first node')
        self.l('Second Simple line')
        self.assertStoredC('''
"1,","0,"test_two_hide2_parents,"tests/writer.py,"log,"Simple line
"2,","0,"test_two_hide2_parents,"tests/writer.py,"a_log,"second,"Open first node
"3,"2,"0,"test_two_hide2_parents,"tests/writer.py,"log,"First line inside ""first""
"4,"2,"0,"test_two_hide2_parents,"tests/writer.py,"c_log,"second,"Close first node
"5,","0,"test_two_hide2_parents,"tests/writer.py,"log,"Second line inside ""first""
"6,","0,"test_two_hide2_parents,"tests/writer.py,"log,"Second Simple line''')

if __name__ == '__main__':
    unittest.main()

