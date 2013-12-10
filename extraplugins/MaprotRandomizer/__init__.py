import collections,random

import acserver
from core.events import eventHandler
from core.maps import OfficialMaps,ServerMaps,IncomingMaps
from core.modes import *

maptypes = ['official']
mapnum = 50
genericmodes = [GMODE_DEATHMATCH,GMODE_SURVIVOR,GMODE_PISTOLFRENZY,GMODE_LASTSWISSSTANDING,GMODE_ONESHOTONEKILL,GMODE_HUNTTHEFLAG]

def main(plugin):
    global maptypes, mapnum
    
    conf = plugin.getConf({'maptypes':'official','mapnum':'50'})
    
    maptypes = conf.get('Settings', 'maptypes').split()
    mapnum = conf.getint('Settings', 'mapnum')
    
@eventHandler('initEnd')
def initend():
    allmaps = collections.deque()
    if 'official' in maptypes:
        allmaps.extend(OfficialMaps)
    if 'server' in maptypes:
        allmaps.extend(ServerMaps)
    if 'incoming' in maptypes:
        allmaps.extend(IncomingMaps)
    
    if not len(allmaps):
        return
    
    acserver.clearMaprot()
    random.shuffle(allmaps)
    
    for i in xrange(mapnum):
        if i%len(allmaps):
            random.shuffle(allmaps)
            
        acserver.addMapToRot(allmaps[1], random.choice(genericmodes), random.randint(5,8), 1)
        allmaps.rotate(1)