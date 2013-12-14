import acserver
from core.events import eventHandler, policyHandler
from core.plugins import plugins
from core.consts import *

enabled = False
nextDamage = 0
damageInterval = 300

def issueDamageUpdate():
    for cn in acserver.getClients():
        cl = acserver.getClient(cn)
        if cl == None:
            continue
            
        if cl['state'] == CS_ALIVE:
            acserver.damageClient(cn,cn,max(2,cl['health']*0.03))
        
        acserver.setClient(cn,points=cl['health'])
    
@eventHandler('serverExtension')
def serverext(cn,ext,ext_text):
    global enabled, clientHealth, nextDamage
    if ext == "enableVampire":
        if auth.hasPermission(cn, "serverOp"):
            enabled = True
            acserver.msg("\f9Vampire is enabled!")
            nextDamage = acserver.getServMillis() + damageInterval
        else:
            acserver.msg("\f3You don't have access to that command!",cn)

@eventHandler('serverTick')
def serverTick(gamemillis, servmillis):
    global enabled, nextDamage
    if enabled:
        if nextDamage <= servmillis:
            issueDamageUpdate()
            nextDamage += damageInterval

@policyHandler('clientDamage')
def clientdamage(acn, tcn, gun, damage, gib):
    global enabled, clientHealth
    if acn == tcn:
        return False
    
    acl = acserver.getClient(acn)
    addedhp = 0
    if gun == GUN_KNIFE:
        tcl = acserver.getClient(tcn)
        if tcl['health'] > 200: #If the health is more than 200, we can have a zap
            acserver.killClient(acn,tcn,1,GUN_KNIFE)
        else:
            acserver.killClient(acn,acn,1,GUN_KNIFE)
    else:
        addedhp = damage/3
    if acl['state'] == CS_ALIVE:
        acserver.setClient(acn,health=acl['health']+addedhp)
        acserver.damageClient(acn,acn,0)
    
#Lets make the plugin loader happy.
def main(plugin):
    pass

@eventHandler('initEnd')
def initend():
    global auth
    auth = plugins['Authentication'].module