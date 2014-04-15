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

DEBUG = False

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
            deps = conf.get('Plugin', 'depends')
            if deps != "":
                self.depends = set(deps.split(','))
            else:
                self.depends = set()
        except NoOptionError:
            acserver.log(":     Invalid config for %s"%self.path,ACLOG_WARNING)
            self.isenabled = False
        del conf
        
        self.__dependname = os.path.basename(self.path)
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
    
    ignoredplugins = Config['acserver']['ignoredplugins'].split()
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
    
    
    name_to_deps = dict( (p,set(plugins[p].depends)) for p in plugins )
    
    if DEBUG:
        for name,deps in name_to_deps.iteritems():
            for parent in deps:
                print("%s -> %s;" %(name,parent))
    
    batches = []
    
    while name_to_deps:
        ready = {name for name, deps in name_to_deps.iteritems() if not deps}
        
        if not ready:
            acserver.log("Circular dependencies or missing plugin found!",ACLOG_ERROR)
            acserver.log("No plugins loaded!",ACLOG_ERROR)
            return
            
            
        for name in ready:
            del name_to_deps[name]
        for deps in name_to_deps.itervalues():
            deps.difference_update(ready)

        batches.append( {plugins[name] for name in ready} )
    
    
    deadplugins = []
    for batch in batches:
        for plugin in batch:
            acserver.log(":   + Loading plugin %s"%plugin.name)
            broken = False
            for dep in plugin.depends:
                if dep in deadplugins:
                    deadplugins.append(plugin.name)
                    acserver.log(" Failed loading plugin (dependancy errors): %s"%plugin.name,ACLOG_WARNING)
                    broken = True
                    
            if not broken and not plugin.loadModule():
                acserver.log(" Failed loading plugin (plugin errors): %s"%plugin.name,ACLOG_WARNING)
                deadplugins.append(plugin.name)
    
    for plugin.name in deadplugins:
        del plugins[plugin.name]
    
    acserver.log("Loaded plugins: %s"%", ".join(plugins.keys()))
            
def reloadPlugins():
    acserver.log("Reloading Plugins:")
    for p in plugins.values():
        p.unloadModule()
    for p in plugins.values():
        p.loadModule()
        
def plugin(name):
    return plugins[name].module
