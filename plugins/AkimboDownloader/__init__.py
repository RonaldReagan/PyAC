import sys, re, subprocess, requests, os, threading, Queue
from StringIO import StringIO
from zipfile import ZipFile

import acserver
from core.events import eventHandler
from core.plugins import plugins
from core.logging import *

preferred_host = None
download_queue = Queue.Queue()
message_queue = Queue.Queue()
download_thread = None
sources = ['packages.ac-akimbo.net', 'de.ac-akimbo.net', 'us.ac-akimbo.net']
url_string = "http://%s/packages/maps/%s.cgz.zip"
local_maps_path = os.path.join('.','packages','maps','servermaps')

def findbesthost():
    ping_re = r'round-trip min/avg/max/stddev = (?P<min>[-+]?[0-9]*\.?[0-9]+)/(?P<avg>[-+]?[0-9]*\.?[0-9]+)/(?P<max>[-+]?[0-9]*\.?[0-9]+)/(?P<stddev>[-+]?[0-9]*\.?[0-9]+) ms'
    ping_re = re.compile(ping_re)

    responses = {}
    
    acserver.log("AkimboDownloader: Checking for the best host...")
    for host in sources:
        if sys.platform == 'win32': #There is a bit different of a format for windows, and I can't get my hands on a machine to figure out everything about it and test.
            #do ping command here
            return sources[0]
        else:
            ping = subprocess.Popen(["ping", "-c1", "-s2048", host], stdout=subprocess.PIPE).stdout.read()
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
    global download_thread
    if ext == "getmap":
        if auth.hasPermission(cn, "getMap"):
            maps = ext_text.split()
            acserver.log("AkimboDownloader: Download request from user %s cn(%d), maps: %s"%(auth.AuthenticatedClients[cn].name,cn,",".join(maps)))
            acserver.msg("\f2Attempting to download: %s"%(",".join(maps)),cn)
            
            for m in maps:
                download_queue.put((m,cn))
                
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

def downloadThreadFunc():
    global download_queue, message_queue
    while True:
        mapname,cn = download_queue.get()
        
        rcode = downloadMap(mapname)
        if rcode != 200:
            message_queue.put({'text':"AkimboDownloader: Error downloading %s, status code: %d"%(mapname,rcode),'type':'log'})
            message_queue.put({'text':"\f3Error downloading %s, status code: %d"%(mapname,rcode),'cn':cn, 'type':'msg'})
        else:
            message_queue.put({'text':"AkimboDownloader: Downloaded map %s"%(mapname),'type':'log'})
            message_queue.put({'text':"\f2Downloaded map %s successfuly!"%(mapname),'cn':cn, 'type':'msg'})
        
        download_queue.task_done()

#Lets make the plugin loader happy.
def main(plugin):
    global preferred_host, download_thread
    preferred_host = findbesthost()
    
    download_thread = threading.Thread(None, target=downloadThreadFunc)
    download_thread.start()
    acserver.log("AkimboDownloader: Setting preferred host to: %s"%preferred_host)

@eventHandler('initEnd')
def initend():
    global auth
    auth = plugins['Authentication'].module
    auth.addPermissionIfMissing("getMap","Allows a user to make the server download a map from akimbo. Warning: This is non-threaded and will cause the server to hang.")
    auth.addPermissionIfMissing("rmMap","Allows a user to delte a map from servermaps.")

@eventHandler('serverTick')
def servertick(gm,sm):
    try:
        msg = message_queue.get(False)
    except Queue.Empty:
        return
    
    if msg['type'] == 'log':
        acserver.log(msg['text'])
    elif msg['type'] == 'msg':
        acserver.msg(msg['text'], msg['cn'])
        