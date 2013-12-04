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
        acserver.log("No users exist, initalizing database.")
        
        acserver.log(":  Creating root user.")
        session.add(db.makeUser("root","pyacserver",""),ACLOG_VERBOSE)
        
        for perm in [('listUsers',"Allows the user to view all other users."),('addUser',"Allows the user create new users")]:
            acserver.log(":  Adding permission %s"%perm[0],ACLOG_VERBOSE)
            session.add(db.makePermission(*perm))
        
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

def hasPermission(cn,perm):
    """
        Checks cn to see if they have the specified permission.
        Returns True if they do or user is Root.
        Returns False if they don't or the cn isn't authenticated.
    """
    if cn not in AuthenticatedClients:
        return False
    
    acserver.log("%d %s %s"%(AuthenticatedClients[cn].id,AuthenticatedClients[cn].name,AuthenticatedClients[cn].email))
    if AuthenticatedClients[cn].id == 1:
        return True
    else:
        return perm in map(lambda p: p.name, AuthenticatedClients[cn].permissions)

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
        
    if ext == "adduser":
        if hasPermission(cn,'addUser'):
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
        else:
            acserver.msg("\f3You don't have access to that command!",cn)
    
    if ext == "listusers":
        if hasPermission(cn,'listUsers'):
            acserver.msg("\fHUser List:",cn)
            for usr in session.query(db.User).all():
                if usr.id == AuthenticatedClients[cn].id:
                    acserver.msg("%d) \fQ%s \f5- \fI%s \f5: {\fN%s\f5}"%(usr.id, usr.name,usr.email,"\f5, \fN".join(map(lambda p: p.name, usr.permissions))),cn)
                else:
                    acserver.msg("%d) \fR%s \f5- \fI%s \f5: {\fN%s\f5}"%(usr.id, usr.name,usr.email,"\f5, \fN".join(map(lambda p: p.name, usr.permissions))),cn)
        
            acserver.msg("\fHEnd User List.",cn)
        else:
            acserver.msg("\f3You don't have access to that command!",cn)
    
    if ext == "grantperm":
        args = ext_text.split()
        if len(args) != 2:
            acserver.msg("\f9Invalid arguments to grantperm", cn)
            return
            
        username,permname = args
        
        try:
            user = db.getUser(session,username)
        except NoResultFound:
            acserver.msg("\f3User not found!",cn)
            return
        
        try:
            perm = db.getPerm(session,permname)
        except NoResultFound:
            acserver.msg("\f3Permission does not exist!",cn)
            return
        
        if perm in user.permissions:
            acserver.msg("\f3User already has that permission!",cn)
            return
        else:
            user.permissions.append(perm)
            session.commit()
            acserver.msg("\fJPermission granted successfully!",cn)
            

@eventHandler('clientDisconnect')
def clientdisconect(cn,reason):
    if cn in AuthenticatedClients:
        del AuthenticatedClients[cn]

# main()