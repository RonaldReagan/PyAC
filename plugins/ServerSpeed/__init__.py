import acserver
from core.events import eventHandler
from core.plugins import plugins

auth = None

mpt_total = 0
mpt_last = 0
mpt_count = 0
mpt_millis = 0
counter = False

def mpt_to_tps(mpt):
    return 1000.0/mpt

@eventHandler('serverExtension')
def serverext(cn,ext,ext_text):
    if ext == "tps":
        if auth.hasPermission(cn, "useTPS"):
            acserver.msg("\fBCurrent TPS: \f9%d\fB, Average: \f9%.2f"%(mpt_to_tps(mpt_last),mpt_to_tps(float(mpt_total)/mpt_count)),cn)
        else:
            acserver.msg("\f3You don't have access to that command!",cn)

@eventHandler('serverTick')
def serverTick(gamemillis, servmillis):
    global mpt_total, mpt_count, mpt_last, mpt_millis
    
    if not counter:
        return
        
    if mpt_millis == -1:
        mpt_millis = servmillis
    else:
        diff = servmillis - mpt_millis
        mpt_total += diff
        mpt_count += 1
        mpt_last = diff
        mpt_millis = servmillis

#Lets make the plugin loader happy.
def main(plugin):
    pass

@eventHandler('initEnd')
def initend():
    global auth, counter
    auth = plugins['Authentication'].module
    auth.addPermissionIfMissing("useTPS","Allows a user to use the tps command")
    counter = True