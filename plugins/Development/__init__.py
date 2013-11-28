import acserver
from core.logging import *
from core.events import eventHandler, policyHandler
acserver.log("Wee! Development!",ACLOG_INFO)

@eventHandler('serverExtension')
def serverext(cn,ext,ext_text):
    acserver.log('SRVEXT from(%d): /%s "%s"'%(cn,ext,ext_text))

@eventHandler('clientDisconnect')
def serverext(cn,reason):
    acserver.log('Disc (%d), Reason: %d'%(cn,reason))

@eventHandler('clientConnect')
def serverext(cn,discreason):
    acserver.log('Connect (%d), DiscReason: %d'%(cn,discreason))
    if discreason == -1:
        acserver.msg("Welcome to our server!", cn)