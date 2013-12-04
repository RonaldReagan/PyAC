from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.schema import Table

import bcrypt

Base = declarative_base()

def setup(dbtype, url, user, pwd, databasename):
    """
        Sets up the engine according to the settings provided. Thus far can set
        up 'sqlite3' and 'mysql' databases.
        
        Returns the engine
    """
    
    if dbtype == "sqlite3":
        engine = create_engine('sqlite:///%s'%url)
    elif dbtype == "mysql":
        engine = create_engine('mysql://%s:%s@%s/%s'%(user,pwd,url,databasename), pool_recycle=3600)
     
    Base.metadata.create_all(engine)
    
    return engine

association_table = Table('userspermissions', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True)
    password = Column(String(60))
    email = Column(String(64))
    permissions = relationship("Permission",secondary="userspermissions")
    
    def checkPassword(self, pwd):
        """
            Returns True if pwd matches user's hashed password. False if it doesn't.
        """
        hashed = bcrypt.hashpw(pwd.encode('ascii', 'ignore'),self.password.encode('ascii', 'ignore'))
        return hashed == self.password
    
    def setPassword(self,pwd):
        """
            Sets the users's password.
            Use this method as it incorperates bcrypt for password storage
        """
        self.password = bcrypt.hashpw(pwd,bcrypt.gensalt())

class Permission(Base):
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    description = Column(String(255))
    
def makePermission(name,desc):
    """
        Returns a Permission object.
        
        Convience method for creating a permission.
    """
    p = Permission()
    p.name = name
    p.description = desc[:255]
    return p

def makeUser(name,password,email):
    """
        Returns User object.
        
        Just a cute shortcut to creating a user, does all of the password
        hashing for you.
        
        password needs to be plaintext.
        
        TODO: make errors if username is taken (or similar things)
    """
    usr = User()
    usr.name = name
    usr.setPassword(password)
    usr.email = email
    
    return usr

def getUser(session, username):
    return session.query(User).filter(User.name==username).one()

def getPerm(session, pname):
    return session.query(Permission).filter(Permission.name==pname).one()
    
if __name__ == "__main__":
    """
        Interactive prompt for database manipulation.
    """
    import sys
    from sqlalchemy.orm import sessionmaker
    from ConfigParser import ConfigParser
    
    conf = ConfigParser({'db_url':'users.db','db_user':'','db_pwd':'','db_type':'sqlite3','db_database':''})
    conf.read(sys.argv[1])
    
    DBURL = conf.get('Settings', 'db_url')    
    DBType = conf.get('Settings', 'db_type')
    DBUser = conf.get('Settings', 'db_user')
    DBPWD = conf.get('Settings', 'db_pwd')
    DBDataBase = conf.get('Settings', 'db_database')
    
    engine = setup(DBType,DBURL,DBUser,DBPWD,DBDataBase)
    session = sessionmaker(bind=engine)()
    
    print("Starting up interactive database manager.")
    while True:
        cmd = raw_input('> ').lower()
        if cmd in ['q','quit','exit','bye']:
            if cmd == 'bye':
                print("Bye!")
            break
        elif cmd in ['h','help']:
            print("Possible commands:")
            print("   quit,help,addusr")
        elif cmd == 'addusr':
            print("Adding User:")
            name = ""
            pwd = ""
            email = ""
            while not name:
                name = raw_input("- Username: ")
            while not pwd:
                pwd = raw_input("- Password: ")
            while not email:
                email = raw_input("- Email: ")
            
            session.add(makeUser(name,pwd,email))
            session.commit()
        elif cmd == 'listusr':
            for usr in session.query(User).all():
                print("%s - %s :: {%s}"%(usr.name,usr.email,",".join(map(lambda p: p.name, usr.permissions))))
        elif cmd == 'addperm':
            print("Adding Permission:")
            name = ""
            while not name:
                name = raw_input("- Permission name: ")
            
            p = Permission()
            p.name = name
            session.add(p)
            session.commit()
            print("Added: %d - %s"%(p.id, p.name))
        elif cmd == 'usrpermadd':
            pname = ""
            uname = ""
            while not uname:
                uname = raw_input("- User name: ")
            while not pname:
                pname = raw_input("- Permission name: ")
            
            try:
                usr = getUser(session,uname)
            except NoResultFound:
                print("No user by that name")
                continue
            
            try:
                perm = session.query(Permission).filter(Permission.name==pname).one()
            except NoResultFound:
                print("No permission by that name")
                continue
            
            usr.permissions.append(perm)
            session.commit()