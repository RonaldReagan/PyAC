import os

from ConfigParser import ConfigParser, NoOptionError

import acserver
from core.consts import *

cmdOpts = acserver.getCmdLineOptions()
configLocation = cmdOpts['py_global_config']

#Public interface, values defined here are defaults
Config = {
    'acserver': {
        'ignoredplugins':'',
        }
    }

conf = ConfigParser()
if os.path.exists(configLocation):
    acserver.log(":   + Loading python global config file: %s"%configLocation)
    conf.read(configLocation)
    if not conf.has_section('acserver'):
        acserver.log("Invalid config file: Make sure you include a section 'acserver'",ACLOG_ERROR)
    else:
        for sec in conf.sections():
            for i in conf.items(sec):
                key,value = i
                Config[sec][key] = value
        
else:
    acserver.log("Could not find global config file, writing default to %s"%configLocation,ACLOG_WARNING)
    
    for sec in Config:
        conf.add_section(sec)
    
        #Copy over the defaults
        for key in Config[sec]:
            conf.set(sec, key, Config[sec][key])
    
    with open(configLocation,'w') as f:
        conf.write(f)