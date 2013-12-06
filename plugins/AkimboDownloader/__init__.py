import sys, re, subprocess, requests, os
from StringIO import StringIO
from zipfile import ZipFile

import acserver
from core.events import eventHandler
from core.plugins import plugins
from core.logging import *

preferred_host = None
sources = ['packages.ac-akimbo.net', 'de.ac-akimbo.net', 'us.ac-akimbo.net']
url_string = "http://%s/packages/maps/%s.cgz.zip"
local_maps_path = os.path.join('.','packages','maps','servermaps')

def findbesthost():
    ping_re = r'round-trip min/avg/max/stddev = (?P<min>[-+]?[0-9]*\.?[0-9]+)/(?P<avg>[-+]?[0-9]*\.?[0-9]+)/(?P<max>[-+]?[0-9]*\.?[0-9]+)/(?P<stddev>[-+]?[0-9]*\.?[0-9]+) ms'
    ping_re = re.compile(ping_re)

    responses = {}
    for host in sources:
        if sys.platform == 'win32': #There is a bit different of a format for windows, and I can't get my hands on a machine to figure out everything about it and test.
            #do ping command here
            return sources[0]
        else:
            ping = subprocess.Popen(["ping", "-c1", host], stdout=subprocess.PIPE).stdout.read()
            m = ping_re.search(ping)
            if m != None:
                avg = m.groupdict()['avg']
                responses[host] = float(avg)

    return min(responses)

def downloadMap(mapname):
    global preferred_host
    if preferred_host == None:
        preferred_host = findbesthost()
    
    host = preferred_host
        
    fullurl = url_string%(host,mapname)
    r = requests.get(fullurl)
    if r.status_code != 200:
        return r.status_code
        
    acmap = ZipFile(StringIO(r.content))
    for name in acmap.namelist():
        acmap.extract(name,local_maps_path)
    
    return r.status_code

@eventHandler('serverExtension')
def serverext(cn,ext,ext_text):
    if ext == "getmap":
        if auth.hasPermission(cn, "getMap"):
            maps = ext_text.split()
            acserver.log("AkimboDownloader: Download request from user %s cn(%d), maps: %s"%(auth.AuthenticatedClients[cn].name,cn,",".join(maps)))
            for mapname in maps:
                rcode = downloadMap(mapname)
                if rcode != 200:
                    acserver.log("AkimboDownloader: Error downloading %s, status code: %d"%(mapname,rcode),ACLOG_ERROR)
                    acserver.msg("\f3Error downloading %s, status code: %d"%(mapname,rcode),cn)
                else:
                    acserver.log("AkimboDownloader: Downloaded map %s"%(mapname))
                    acserver.msg("\f2Downloaded map %s successfuly!"%(mapname),cn)
        else:
            acserver.msg("\f3You don't have access to that command!",cn)
    
    if ext == "removemap":
        if auth.hasPermission(cn, "rmMap"):
            maps = ext_text.split()
            acserver.log("AkimboDownloader: Delete request from user %s cn(%d), maps: %s"%(auth.AuthenticatedClients[cn].name,cn,",".join(maps)))
            for mapname in maps:
                try:
                    os.remove(os.path.join(local_maps_path,os.path.basename(mapname)+'.cgz'))
                except OSError:
                    acserver.msg("\f3Error deleting %s."%(mapname),cn)
                    acserver.log("AkimboDownloader: Map delete failed %s, full path: %s"%(mapname,os.path.join(local_maps_path,os.path.basename(mapname))))
                    continue
                
                try:
                    os.remove(os.path.join(local_maps_path,os.path.basename(mapname)+'.cfg'))
                except OSError:
                    pass #Its totally normal not to have a cfg
                
                
                acserver.msg("\f2Map %s deleted"%(mapname),cn)
                acserver.log("AkimboDownloader: Deleted map %s"%(mapname))
        else:
            acserver.msg("\f3You don't have access to that command!",cn)

#Lets make the plugin loader happy.
def main(plugin):
    global preferred_host
    preferred_host = findbesthost()
    acserver.log("AkimboDownloader: Setting preferred host to: %s"%preferred_host)

@eventHandler('initEnd')
def initend():
    global auth
    auth = plugins['Authentication'].module
    auth.addPermissionIfMissing("getMap","Allows a user to make the server download a map from akimbo. Warning: This is non-threaded and will cause the server to hang.")
    auth.addPermissionIfMissing("rmMap","Allows a user to delte a map from servermaps/")