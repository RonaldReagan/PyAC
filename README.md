====
PyAC
====

Embeds python into AssaultCube.


  This project is obviously a WIP, and less obviously more of a toy than
anything. However if any interest is sparked or anyone else wants to
contribute, I may get more serious about this project. This is not
guaranteed to compile on anything but OSX as I do not test regularly enough on other systems. Hopefully it will be stable on other operating systems, I'd like to think my programming isn't that bad.

  This repository is based off of 1.2 until I get a stable version, and then I will update and continue updating with the main AC repository. Some of the code base is based off of a similar project, xsbs, which can be found here: https://github.com/greghaynes/xsbs

  This follows all the same licenses as AC does. My code isn't anything
special, so feel free to use what I added in anyway you want.

--------
Building
--------

The current build system is scons which can be found here: http://www.scons.org/

cd into ./source/src
To build (on *nix):

	$ scons

To clean (on *nix):

	$ scons -c

To make install (on *nix):

	$ scons install

To build, and then run the server (on *nix):

	$ scons install
	$ cd ../../
	$ ./bin/native_server


---
API
---

This will server as the API documentation, until a better solution is had.

###Events
Events are functions that get called when actions happen.

####Events
With normal these normal events, the return value is ignored.

* **initEnd**() - *Called when the init phase of server startup has finished (all config files loaded). Remember that the plugin gets loaded before any other initialization occurs.*
* **serverExtension**(int cn, str ext, str ext_text) - *Called when a user uses a /serverextension, and no matching server extensions have been found.*
* **clientDisconnect**(int cn, int reason) - *Called when a client disconnects for any reason. The specific reason is given by the argument 'reason'*
* **clientConnect**(int cn, int discreason) - *Called when a client connects. If the client fails to connect (matches blacklist, offends a whitelist entry), then the client will be immediately disconnected and the reason for disconnection will be given in discreason.*
* **serverTick**(int gamemillis, int servermillis) - *Called once per server frame. gamemillis is the number of millis in the game, servermillis is the total number of millis since server startup.*

####PolicyEvents
With these policy events, the return value is used to alter the action of the server. If boolean, True will block the event, False will leave it unchanged.

* **clientSpawn**(int cn) - *Triggered when a client spawns.*
* **clientDeath**(int acn, int tcn, int gun, int damage) - *Triggered when a client dies*
* **clientSay**(int cn, str text, bool isteam, bool isme) - *Triggered when a client talks in the server*
* **masterRegister**(str masterhost, int masterport) - *Triggered when the server tries to register with the masterserver*

###Modules

####acserver
Main module for server interaction.

Methods defined here:

* **acserver.log**(str msg, [int level]) - *Logs a message, level defaults to info.*
* **acserver.msg**(str msg, [int cn]) - *Sends a message to a client, if cn is -1 (default) then it sends the message to all clients.*
* **acserver.killClient**(int acn, int tcn [bool (int) gib, int weap]) - *Makes it as if acn killed tcn with given weapon, and specifies if it was gib or not*
* **acserver.spawnClient**(int cn, int health, [int armour, int ammo, int mag, int weapon, int primaryweapon]) - *Spawn client with specified starting stats.*
* **acserver.getClient**(int cn) - *Returns a dictionary with client stats*
* **acserver.getCmdLineOptions**() - *Returns a dictionary with all of the server commandline options.* **TODO: Better name?**

####core
Core functionality. These are modules that are required for server functionality.

####core.events

####core.plugins
This plugin should not be used manually.

####core.logging
This module defines constants used with *acserver.log*