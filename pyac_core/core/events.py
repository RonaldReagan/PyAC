import sys
import traceback

from twisted.internet import reactor

import acserver
from core.consts import *

class EventManager:
    def __init__(self):
        self.events = {}
    def connect(self, event, func):
        try:
            self.events[event].append(func)
        except KeyError:
            self.events[event] = []
            self.connect(event, func)
    def trigger(self, eventname, args=()):
        try:
            for event in self.events[eventname]:
                try:
                    event(*args)
                except:
                    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
                    acserver.log('Uncaught exception occured in event handler.',ACLOG_ERROR)
                    for line in traceback.format_exc().split('\n'):
                        acserver.log(line,ACLOG_ERROR)
        except KeyError:
            pass

class PolicyEventManager(EventManager):
    def __init__(self):
        EventManager.__init__(self)
    def trigger(self, event, args=()):
        blockevent = False
        try:
            for event in self.events[event]:
                blockevent = event(*args) or blockevent
        except KeyError:
            return False
            
        return blockevent

server_events = EventManager()
policy_events = PolicyEventManager()

def registerServerEventHandler(event, func):
    '''Call function when event has been executed.'''
    server_events.connect(event, func)

class eventHandler(object):
    '''Decorator which registers a function as an event handler.'''
    def __init__(self, name):
        self.name = name
    def __call__(self, f):
        self.__doc__ = f.__doc__
        self.__name__ = f.__name__
        registerServerEventHandler(self.name, f)
        return f

def triggerServerEvent(event, args):
    '''Trigger event with arguments.'''
    server_events.trigger(event, args)

def registerPolicyEventHandler(event, func):
    '''Call function when policy event has been executed.'''
    policy_events.connect(event, func)

class policyHandler(object):
    '''Decorator which registers a function as a policy event handler.'''
    def __init__(self, name):
        self.name = name
    def __call__(self, f):
        self.__doc__ = f.__doc__
        self.__name__ = f.__name__
        registerPolicyEventHandler(self.name, f)
        return f

def triggerPolicyEvent(event, args):
    '''Trigger policy event with arguments.'''
    return policy_events.trigger(event, args)

@eventHandler('serverTick')
def update(gm,sm):
    reactor.runUntilCurrent()
    reactor.doIteration(0)

@eventHandler('reload')
def onReload():
    server_events.events.clear()

reactor.startRunning()