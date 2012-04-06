import sys
def unicoder(line):
    try:
        try:
            return unicode(line)
        except UnicodeDecodeError:
            return str(line).decode('utf-8')
    except Exception,e:
        return u'*** EXCEPTION ***'+str(e)

def import_name(line):
    line = line.split('.')
    mname = '.'.join(line[:-1])
    if mname in sys.modules:
        mname = sys.modules[mname]
    else:
        __import__(mname)
        mname = sys.modules[mname]
    return getattr(mname,line[-1])

def arr_lambda_by_name(items,mod):
    ret = []        
    for item in items:
        if isinstance(item, (str,unicode)):
            try:
                item.index('.')
            except ValueError:
                item = getattr(mod, item)
            else:
                item = import_name(item)
        ret.append(item)
    return ret

def get_trio_log(logger,logname):
    return getattr(logger,logname),getattr(logger,'a_'+logname),getattr(logger,'c_'+logname)

def arr_funcs_call(items,*args,**kwargs):
    ret = []
    for item in items:# self.func_fields:
        ret.append(item(*args,**kwargs))
    return ret