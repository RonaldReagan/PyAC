"""
    plugins.py
    
    Loads plugins for use in PyAC
    
    Modified version of xsbs plugins.py. Original can be found at:
    https://github.com/greghaynes/xsbs/blob/master/src/pyscripts/xsbs/plugins.py
    
    Licensed under GPLv2
"""
import os
import sys
import traceback
from ConfigParser import ConfigParser, NoOptionError

import acserver
from core.config import Config
from core.consts import *

plugins = {}
paths = ['./plugins']

class Plugin:
    def __init__(self, path, config_path, forcedisabled):
        self.path = path
        self.config_path = config_path
        
        conf = self.getConf()
        
        self.isenabled = True
        try:
            self.isenabled = (conf.get('Plugin', 'enable') == 'yes')
            self.name = conf.get('Plugin', 'name')
            self.version = conf.get('Plugin', 'version')
            self.author = conf.get('Plugin', 'author')
        except NoOptionError:
            self.isenabled = False
        del conf
        
        if forcedisabled:
            self.isenabled = False
            
    def loadModule(self):
        if self.isenabled:
            try:
                self.module = __import__(os.path.basename(self.path))
            except:
                exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
                acserver.log('Uncaught exception occured when loading %s. Disabling plugin.'%self.name,ACLOG_ERROR)
                for line in traceback.format_exc().split('\n'):
                    acserver.log(line,ACLOG_ERROR)
                return False
                
            try:
                #Reference it first to catch it not existing. Not some sort of internal error.
                main = self.module.main 
            except AttributeError:
                acserver.log("No main function in %s"%self.path,ACLOG_WARNING)
                return False
            
            main(self) #Call the main, passing the reference to the module.
            
            return True
        else:
            return False
                
    def unloadModule(self):
        if self.isenabled:
            del self.module
    def enabled(self):
        return self.isenabled
    
    def getConf(self,defaults={}):
        conf = ConfigParser(defaults)
        conf.read(self.config_path)
        return conf

def loadPlugins():
    plugins.clear()
    
    ignoredplugins = Config['ignoredplugins'].split()
    for path in paths:
        files = os.listdir(path)
        for file in files:
            dirpath = os.path.join(path,file)
            config_path = os.path.join(dirpath,"plugin.conf")
            if os.path.isdir(dirpath) and os.path.exists(config_path):
                if os.path.basename(dirpath) in ignoredplugins:
                    forcedisabled = True
                else:
                    forcedisabled = False
                    
                p = Plugin(dirpath, config_path, forcedisabled)
                
                if p.isenabled:
                    plugins[p.name] = p
                else:
                    acserver.log(":   - Skipping plugin %s"%p.path)
    
    deadplugins = []
    for pname in plugins:
        plugin = plugins[pname]
        acserver.log(":   + Loading plugin %s"%pname)
        if not plugin.loadModule():
            acserver.log(" Failed loading plugin %s"%pname,ACLOG_WARNING)
            deadplugins.append(pname)
    
    for pname in deadplugins:
        del plugins[pname]
    
    acserver.log("Loaded plugins: %s"%", ".join(plugins.keys()))
            
def reloadPlugins():
    acserver.log("Reloading Plugins:")
    for p in plugins.values():
        p.unloadModule()
    for p in plugins.values():
        p.loadModule()
