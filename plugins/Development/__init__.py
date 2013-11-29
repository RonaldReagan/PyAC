import acserver
from core.logging import *
from core.events import eventHandler, policyHandler
from core.plugins import reloadPlugins
acserver.log("Wee! Development! Module is initalized!",ACLOG_INFO)

blockDeaths = False
blockSpawns = False

@eventHandler('serverExtension')
def serverext(cn,ext,ext_text):
    global blockDeaths, blockSpawns
    acserver.log('SRVEXT from(%d): /%s "%s"'%(cn,ext,ext_text))
    if ext == "kill":
        acserver.killClient(cn,cn)
    if ext == "ip":
        tcn = int(ext_text)
        acserver.msg("IP: \f1%s"%acserver.getClient(tcn)['hostname'],cn)
    if ext == "spawn":
        tcn,health,armour,ammo,mag,weapon,primaryweapon = map(int,ext_text.split()) #/serverextension spawn "0 55 5555 12 12 2 1"
        acserver.log(repr(acserver.spawnClient(tcn,health,armour,ammo,mag,weapon,primaryweapon)))
    if ext == "reload":
        reloadPlugins()
    if ext == "block":
        if ext_text.lower() =='deaths':
            blockDeaths = True
        if ext_text.lower() =='spawns':
            blockSpawns = True
    if ext == "allow":
        if ext_text.lower() =='deaths':
            blockDeaths = False
        if ext_text.lower() =='spawns':
            blockSpawns = False

@eventHandler('clientDisconnect')
def serverext(cn,reason):
    acserver.log('Disc (%d), Reason: %d'%(cn,reason))

@eventHandler('clientConnect')
def serverext(cn,discreason):
    acserver.log('Connect (%d), DiscReason: %d'%(cn,discreason))
    if discreason == -1:
        acserver.msg("Welcome to our server!", cn)

@policyHandler('clientDeath')
def clientdeath(acn,tcn,gun,damage):
    if blockDeaths:
        acserver.log('Blocked death of %s'%(acserver.getClient(tcn)['name']))
    return blockDeaths

@policyHandler('clientSpawn')
def clientspawn(cn):
    if blockSpawns:
        acserver.log('Blocked spawn of %s'%(acserver.getClient(cn)['name']))
    return blockSpawns
    
@policyHandler('masterRegister')
def masterRegister(host,port):
    acserver.log('Block master registration.')
    return True