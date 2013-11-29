"""
    plugins.py
    
    Loads plugins for use in PyAC
    
    Modified version of xsbs plugins.py. Original can be found at:
    https://github.com/greghaynes/xsbs/blob/master/src/pyscripts/xsbs/plugins.py
    
    Licensed under GPLv2
"""
import os
from ConfigParser import ConfigParser, NoOptionError

import acserver
from core.config import Config

plugins = {}
paths = ['./plugins']

class Plugin:
    def __init__(self, path, config_path, forcedisabled):
        self.path = path
        conf = ConfigParser()
        conf.read(config_path)
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
            self.module = __import__(os.path.basename(self.path))
    def unloadModule(self):
        if self.isenabled:
            del self.module
    def enabled(self):
        return self.isenabled

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
                    acserver.log(":   + Loaded plugin %s"%p.name)
                else:
                    acserver.log(":   - Skipped plugin %s"%p.path)
                
    for plugin in plugins.values():
        plugin.loadModule()

def reloadPlugins():
    acserver.log("Reloading Plugins:")
    for p in plugins.values():
        p.unloadModule()
    for p in plugins.values():
        p.loadModule()
