import os

import acserver

plugins = {}
paths = ['./plugins']

class Plugin:
    def __init__(self, path):
        self.path = path
        self.name = path
    def loadModule(self):
        self.module = __import__(os.path.basename(self.path))
    def unloadModule(self):
        if self.isenabled:
            del self.module

def loadPlugins():
    plugins.clear()
    for path in paths:
        files = os.listdir(path)
        for file in files:
            dirpath = path + '/' + file
            if os.path.isdir(dirpath):
                p = Plugin(dirpath)
                plugins[p.name] = p
                acserver.log(":   - Loaded plugin %s"%p.name)
                
    for plugin in plugins.values():
        plugin.loadModule()

def reloadPlugins():
    for p in plugins.values():
        p.unloadModule()
    for p in plugins.values():
        p.loadModule()
