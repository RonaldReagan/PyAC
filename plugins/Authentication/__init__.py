from ConfigParser import ConfigParser, NoOptionError

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

import acserver
from core.events import eventHandler
from core.logging import *

from Authentication import database as db

engine = None

AuthenticatedClients = {} #Key: CN, Value: User Class

def main(self):
    global engine
    
    conf = self.getConf({'db_url':'users.db','db_user':'','db_pwd':'','db_type':'sqlite3','db_database':''})
    
    DBURL = conf.get('Settings', 'db_url')    
    DBType = conf.get('Settings', 'db_type')
    DBUser = conf.get('Settings', 'db_user')
    DBPWD = conf.get('Settings', 'db_pwd')
    DBDataBase = conf.get('Settings', 'db_database')
    
    engine = db.setup(DBType,DBURL,DBUser,DBPWD,DBDataBase)
    
    session = _getSession()
    if session.query(db.User).count() == 0:
        acserver.log("No users exist, creating root account.")
        session.add(db.makeUser("root","pyacserver",""))
        session.commit()
        
    session.close()

def _getSession():
    """
        Returns the session
    """
    session = sessionmaker(bind=engine)()
    return session

def getSession(f):
    """
        Decorator, passes the session as the first argument. Closes it
        automatically afterwards
    """
    def wrapper(*args,**kwargs):
        s = _getSession()
        return f(*[s]+list(args),**kwargs)
        s.close()
    return wrapper

@eventHandler('serverExtension')
@getSession
def serverext(session,cn,ext,ext_text):
    if ext == "auth":
        args = ext_text.split()
        if len(args) != 2:
            acserver.msg("\f9Invalid arguments to auth/", cn)
            return
            
        name, pwd = args

        try:
            usr = session.query(db.User).filter(db.User.name==name).one()
        except NoResultFound:
            acserver.msg("\f9Invalid login!",cn)
            return
            
        if usr.checkPassword(pwd):
            AuthenticatedClients[cn] = usr
            acserver.msg("\fJLogin Succeeded!",cn)
            acserver.log("Authenticated client (%d) %s as %s"%(cn,acserver.getClient(cn)['name'],name))
        else:
            acserver.msg("\f9Invalid login!",cn)
        
    
    if ext == "register":
        args = ext_text.split()
        if len(args) != 3:
            acserver.msg("\f9Invalid arguments to register", cn)
            return
        
        name, email, pwd = args
        
        usrcount = session.query(db.User).filter(db.User.name==name).count()
        
        if usrcount:
            acserver.msg("\f9User already exists!",cn)
            session.close()
            return
        
        session.add(db.makeUser(name,pwd,email))
        session.commit()
        acserver.msg("\fJCreated user! Please login now with the credentials you provided.",cn)
    
    if ext == "listusers":
        acserver.msg("\fHUser List:",cn)
        for usr in session.query(db.User).all():
            acserver.msg("\fI%s \f5- \fE%s"%(usr.name,usr.email),cn)
        
        acserver.msg("\fHEnd User List.",cn)

@eventHandler('clientDisconnect')
def clientdisconect(cn,reason):
    if cn in AuthenticatedClients:
        del AuthenticatedClients[cn]

# main()