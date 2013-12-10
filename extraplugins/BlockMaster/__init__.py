import acserver
from core.logging import *
from core.events import policyHandler
    
@policyHandler('masterRegister')
def masterRegister(host,port):
    acserver.log('Blocked master registration.',ACLOG_VERBOSE)
    return True

#Lets make the plugin loader happy.
def main(plugin):
    pass