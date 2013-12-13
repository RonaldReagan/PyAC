import os

from ConfigParser import ConfigParser, NoOptionError

import acserver
from core.consts import *

cmdOpts = acserver.getCmdLineOptions()
configLocation = cmdOpts['py_global_config']

#Public interface, values defined here are defaults
Config = {'ignoredplugins':''
          }

conf = ConfigParser()
if os.path.exists(configLocation):
    acserver.log(":   + Loading python global config file: %s"%configLocation)
    conf.read(configLocation)
    if not conf.has_section('acserver'):
        acserver.log("Invalid config file: Make sure you include a section 'acserver'",ACLOG_ERROR)
    else:
        for i in conf.items('acserver'):
            key,value = i
            Config[key] = value
        
else:
    acserver.log("Could not find global config file, writing default to %s"%configLocation,ACLOG_WARNING)
    conf.add_section('acserver')
    
    #Copy over the defaults
    for key in Config:
        conf.set('acserver', key, Config[key])
    
    with open(configLocation,'w') as f:
        conf.write(f)