import os
def stacksize(fstack,*args,**kwargs):
    return kwargs['stack']
def fname(fstack,*args,**kwargs):
    return fstack.f_code.co_name
def filename(fstack,self,*args,**kwargs):
    filename = fstack.f_code.co_filename

    if self.related_folder and filename.startswith(self.related_folder):
        return filename[len(self.related_folder):]
    return filename
def lineno(fstack,*args,**kwargs):
    return fstack.f_lineno
from datetime import datetime
def strtime(fstack,*args,**kwargs):
    return datetime.now().isoformat()
def pid(fstack,*args,**kwargs):
    return str(os.getpid())
def thread_name(fstack,*args,**kwargs):
    import threading
    return threading.currentThread().getName()
def thread_ident(fstack,*args,**kwargs):
    import threading
    return threading.currentThread().ident
