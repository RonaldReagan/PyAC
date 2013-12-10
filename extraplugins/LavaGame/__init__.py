import acserver
from core.events import eventHandler, policyHandler
from core.plugins import plugins

frames = 0
enabled = False
auth = None
waterlevel = -127

@eventHandler('serverExtension')
def serverext(cn,ext,ext_text):
    global enabled
    if ext == "enableLava":
        if auth.hasPermission(cn, "lavaOp"):
            enabled = True
            acserver.msg("\f9Lava is enabled!")
        else:
            acserver.msg("\f3You don't have access to that command!",cn)
    
    if ext == "disableLava":
        if auth.hasPermission(cn, "lavaOp"):
            enabled = False
            acserver.msg("\f4Lava is disabled!",cn)
        else:
            acserver.msg("\f3You don't have access to that command!",cn)

#Lets make the plugin loader happy.
def main(plugin):
    pass

@eventHandler('initEnd')
def initend():
    global auth
    auth = plugins['Authentication'].module
    auth.addPermissionIfMissing("lavaOp","Allows the user to control the lava game plugin.")

@eventHandler('gameStart')
def gamestart(mapname,mode,gm,gl):
    global waterlevel
    waterlevel = acserver.getMapInfo()['waterlevel']

@eventHandler('serverTick')
def servertick(gm,sm):
    global frames, waterlevel
    frames += 1
    if not enabled:
        return
        
    if frames%10 == 0:
        clients = acserver.getClients()
        if not clients:
            return
        
        for cn in clients:
            cl = acserver.getClient(cn)
            if cl == None:
                continue
                
            z = cl['pos'][2]
            if z < waterlevel and z > -256 and z < 256 and cl['state'] == 0:
                acserver.killClient(cn,cn)