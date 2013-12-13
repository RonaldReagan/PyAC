import threading

import acserver
from core.events import eventHandler, triggerServerEvent
from core.plugins import plugins
from core.consts import *

from IRCBot.irclib import IRCBot, IRCConnection

auth = None
acircbot = None
bot_running = False

settings = {}
    
class ACIRCBot(IRCBot):
    def command_patterns(self):
        return (
            ('/chanmsg', self.evt_chanmsg),
            ('/privmsg', self.evt_privmsg),
            ('/part', self.evt_part),
            ('/join', self.evt_join),
            ('/quit', self.evt_quit),
        )
    
    def evt_chanmsg(self,nick,msg,channel):
        triggerServerEvent("IRC_chanMsg",(self,nick,msg,channel))
    
    def evt_privmsg(self,nick,msg,channel):
        triggerServerEvent("IRC_privMsg",(self,nick,msg))
    
    def evt_part(self,nick,msg,channel):
        triggerServerEvent("IRC_part",(self,nick,channel))
        
    def evt_join(self,nick,msg,channel):
        triggerServerEvent("IRC_join",(self,nick,channel))
        
    def evt_quit(self,nick,msg,channel):
        triggerServerEvent("IRC_quit",(self,nick))

#Lets make the plugin loader happy.
def main(plugin):
    global settings
    
    conf = plugin.getConf({'host':'us.quakenet.org','port':'6667','nick':'acserverbot','channels':'#bottestchan'})
    
    settings['host'] = conf.get('Settings', 'host')
    settings['port'] = conf.getint('Settings', 'port')
    settings['nick'] = conf.get('Settings', 'nick')
    settings['channels'] = conf.get('Settings', 'channels').split()
    
    startIRCBot()

def startIRCBot():
    global acircbot, bot_running
    
    if bot_running:
        return
        
    conn = IRCConnection(settings['host'], settings['port'], settings['nick'])
    
    acircbot = ACIRCBot(conn)
    
    bot_running = conn.connect()
    
    if bot_running:
        channels = settings.get('channels',[])
        for channel in channels:
            conn.join(channel)
    else:
        acserver.log("IRCBOT: Failed to start, disabled")

def stopIRCBot():
    global bot_running
    acircbot.conn.quit()
    acircbot.conn.close()
    
    bot_running = False

@eventHandler('serverTick')
def servertick(gm,sm):
    global bot_running
    if bot_running:
        emsg = acircbot.conn.event_slice()
        if emsg:
            acserver.log(emsg,ACLOG_ERROR)
            bot_running = False

@eventHandler('initEnd')
def initend():
    global auth
    auth = plugins['Authentication'].module
    auth.addPermissionIfMissing("IRCOp","Allows the user to execute basic commands with the IRC Bot.")
    auth.addPermissionIfMissing("IRCController","Allows the user to control the IRC Bot fully.")

@eventHandler('IRC_chanMsg')
def chanmsg(bot,nick,msg,channel):
    bot.msg("\f2[IRC]\f9%s\f5 %s: %s"%(nick,channel,msg))

@eventHandler('serverExtension')
def serverext(cn,ext,ext_text):
    if ext == 'sendirc':
        if not (auth.hasPermission(cn,'IRCOp') or auth.hasPermission(cn,'IRCController')):
            acserver.msg("\f3You don't have access to that command!",cn)
            return
            
        if len(ext_text.split()) < 2:
            acserver.msg("\f9Invalid arguments to sendirc", cn)
            return
        
        chan,msg = ext_text.split(' ',1)
        acircbot.msg(msg,channel=chan)
        acserver.log("IRCBOT: User %s cn(%d) sent messsage to %s: %s."%(auth.AuthenticatedClients[cn].name,cn, chan, msg),cn)
        
    if ext == 'startirc':
        if not auth.hasPermission(cn,'IRCController'):
            acserver.msg("\f3You don't have access to that command!",cn)
            return
            
        if bot_running:
            acserver.msg("\f3The IRC Bot is already running!",cn)
        else:
            startIRCBot()
            acserver.msg("\f1Attempted startup of IRCBot.",cn)
            acserver.log("IRCBOT: Start command issued by user %s cn(%d)."%(auth.AuthenticatedClients[cn].name,cn),cn)
    
    if ext == 'stopirc':
        if not auth.hasPermission(cn,'IRCController'):
            acserver.msg("\f3You don't have access to that command!",cn)
            return
            
        if not bot_running:
            acserver.msg("\f3The IRC Bot isn't running!",cn)
        else:
            stopIRCBot()
            acserver.msg("\f1IRC bot stopped.",cn)
            acserver.log("IRCBOT: Stop command issued by user %s cn(%d)."%(auth.AuthenticatedClients[cn].name,cn),cn)