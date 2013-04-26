#!/usr/bin/python
# coding: utf-8
import sys
import os
import codecs
from datetime import datetime
from ucsvlog.fields import every
from random import randint

from ucsvlog.utils import unicoder, arr_lambda_by_name, arr_funcs_call

import six


class Logger(object):
    # log file template
    action_log_template = None

    # log file name
    action_log_file = None

    # log file handle
    action_log_fh = None

    # file handle buffering
    action_log_buffering = 0

    # time of current append index
    aindex = ''

    # stack of all appended indexes
    aindex_stack = None

    # list of functions to save call informations into logs
    func_fields = None

    def __init__(self,
                 # path ( template ) to log file in file system
                 # copied into action_log_template property
                 # action_log_file = converted real file path
                 # action_log_fh = current filehandle
                 action_log,

                 # list of levels which will be logged
                 # default is ['crt', 'err', 'imp', 'inf', 'log', 'trc', 'dbg']
                 level=None,

                 # the log level which will be used if Logger object used
                 # as function
                 # means glog() is equal to glog.log() in case
                 # default_level = 'log'
                 # stored into def_log_call property as function
                 default_level='log',

                 # list of levels which will be actually saved into
                 # the log file if it is None the all levels will be stored.
                 loglev=None,

                 # list of fields name or function which fill be put
                 # in every log row right after parent index.
                 # list of possible name can be found in ucsvlog.fields.every
                 # but you can also use your own function as string name
                 # of link
                 # this list ['stacksize','fname','filename','lineno']
                 # will be used if None passed
                 # pass an empty list in case you don't want to store call info
                 # stored into same name property, but converted into functions
                 func_fields=None,

                 # using in codes.open(buffering=???)
                 # http://docs.python.org/library/codecs.html#codecs.open
                 # which is the same as for buildin function open
                 # http://docs.python.org/library/functions.html#open
                 # and save into action_log_buffering
                 buffering=0,

                 # related folder is using for save related file paths
                 # in call info
                 # saved into same name property but add '/' at the end
                 # if doesn't have
                 related_folder=None,

                 # True - if you want to store one block in different files.
                 # useful for logging long terms blocks,
                 # like long working cron scripts
                 # False - if you want to store one block in one file
                 # useful in short terms block, like http requests
                 # saved into same name property
                 splitting_blocks=False,

                 # if this value is not None then every row will have
                 # with value as last cell
                 # using in Reader object to be sure that the row is
                 # 100% valid and not broken
                 # saved into same name property
                 close_row=None,
                 ):
        self.splitting_blocks = splitting_blocks
        self.close_row = close_row

        if related_folder is not None:
            related_folder = os.path.abspath(related_folder)
            if not related_folder.endswith('/'):
                related_folder += '/'
        self.related_folder = related_folder

        self.action_log_template = action_log
        self.action_log_buffering = buffering
        self.action_log_file = None
        self.action_log_fh = None

        if loglev is None:
            loglev = [
                    'crt',  # critical error
                    'err',  # error
                    'imp',  # important information
                    'inf',  # information
                    'log',  # base log
                    'trc',  # trace some data
                    'dbg'   # debug information
                    ]
        if level is None:
            level = loglev
        if isinstance(level, int):
            level = loglev[:level]

        if func_fields is None:
            func_fields = ['stacksize', 'fname', 'filename', 'lineno']
        self._aindex_stack = []

        # generate write functions or empty function
        # depends on loglev and level input parameters
        for logname in loglev:
            if logname in level:
                setattr(self, logname, self.lbd_tlog(logname))
                setattr(self, 'a_' + logname, self.lbd_alog(logname))
                setattr(self, 'c_' + logname, self.lbd_clog(logname))
            else:
                setattr(self, logname, lambda *args, **kwargs: None)
                setattr(self, 'a_' + logname, lambda *args, **kwargs: None)
                setattr(self, 'c_' + logname, lambda *args, **kwargs: None)

        self.def_log_call = getattr(self, default_level)

        self.func_fields = arr_lambda_by_name(func_fields, every)

    def _get_aindex_stack(self):
        return self.get_aindex_stack()

    def get_aindex_stack(self):
        return self._aindex_stack

    aindex_stack = property(_get_aindex_stack)

    def __call__(self, data, stack=0):
        return self.def_log_call(data, stack + 1, stack_minus=3)

    def action_log_template_params(self):
        'the dict wich will used to convert log file template to real filename'

        now = datetime.now()
        return {
            'year': now.year,
            'syear': six.text_type(now.year)[2:],
            'month': now.month,
            'day': now.day,
            'hour': now.hour,
            '2_hour': (now.hour / 2) * 2,
            '3_hour': (now.hour / 3) * 3,
            '5_hour': (now.hour / 5) * 5,
            'minute': now.minute,
            '0month': '%0.2d' % now.month,
            '0day': '%0.2d' % now.day,
            '0hour': '%0.2d' % now.hour,

        }

    def init_log_fh(self):
        '''
        init logger filehanle in case a the real file name after
        rendering file template was changed
        init action_log_fh and action_log_file
        '''
        new_action_log_file = self.action_log_template.\
                                format(**self.action_log_template_params())
        if new_action_log_file == self.action_log_file and self.action_log_fh:
            return
        self.action_log_file = new_action_log_file
        if self.action_log_fh is not None:
            self.action_log_fh.close()
        self.action_log_fh = self._init_cur_fh()

    def _init_cur_fh(self):
        return codecs.open(self.action_log_file, 'a', 'utf8',\
                            buffering=self.action_log_buffering)

    def flush(self):
        self.action_log_fh and self.action_log_fh.flush()

    def lbd_tlog(self, logname):
        return lambda data, stack=0, stack_minus=2: \
            self.tlog(logname, data if isinstance(data, (list, tuple))\
                                 else [data], stack + 2,\
                     stack_minus=stack_minus)

    def lbd_alog(self, logname):
        return lambda search, data=None, \
            stack=0: self.alog(search, logname, data, stack + 3)

    def alog(self, search, logname, data=None, stack=3):
        if not self.splitting_blocks and not self.aindex_stack:
            #init for new blocks only for a new file
            self.init_log_fh()

        if data is None:
            params = []
        elif isinstance(data, (list, tuple)):
            params = data
        else:
            params = [data]

        data = self.tlog('a_' + logname, [search] + params, stack,\
                                                     stack_minus=3)
        self.aindex_stack.append([data[0], search])

    def lbd_clog(self, logname):
        return lambda search, data=None, stack=0: \
                        self.clog(search, logname, data, stack + 3)

    def clog(self, search, logname, data, stack=3):
        remove_length = len(self.aindex_stack)

        if data is None:
            params = []
        elif isinstance(data, (list, tuple)):
            params = data
        else:
            params = [data]

        for item in reversed(self.aindex_stack):
            if item[1] == search:
                del self.aindex_stack[remove_length:]
                self.tlog('c_' + logname, [search] + params, stack,\
                           stack_minus=3)
                self.aindex_stack.pop()
                break
            remove_length -= 1
        else:
            #convert to simple log
            self.tlog(logname, [search] + params, stack, stack_minus=3)

    def clear_one_ceil(self, line):
        return unicoder(line).replace('"', '""')

    def clear_one_line(self, data):
        line = u'\n"' + u',"'.join(map(self.clear_one_ceil, data))
        if self.close_row is None:
            return line
        else:
            return line + ',"' + self.close_row

    def store_row(self, data):
        if self.splitting_blocks or self.action_log_fh is None:
            self.init_log_fh()
        self.action_log_fh.write(self.clear_one_line(data))

    def get_parent_record_key(self):
        'get key of parent record for current'
        if not self.aindex_stack:
            return ''
        return self.aindex_stack[-1][0]

    def get_record_time(self):
        'return current time in str'
        return datetime.now().isoformat()

    def gen_record_key(self):
        '''str key'''
        return self.get_record_time() + ';' + str(randint(0, 100))

    def tlog(self, name, params, stack=1, stack_minus=0):
        '''
            Write a single line
        '''
        #import ipdb;ipdb.set_trace()
        arr_row = [self.gen_record_key(), self.get_parent_record_key()] +\
                arr_funcs_call(self.func_fields, sys._getframe(stack), \
                               self, stack=stack - stack_minus) +\
                [name] + params
        self.store_row(arr_row)
        return arr_row
