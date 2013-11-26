PyAC
====

Embeds python into AssaultCube.


  This project is obviously a WIP, and less obviously more of a toy than
anything. However if any interest is sparked or anyone else wants to
contribute, I may get more serious about this project. This is not
guaranteed to compile on anything but OSX as I do not test regularly enough on other systems. Hopefully it will be stable on other operating systems, I'd like to think my programming isn't that bad.

  This repository is based off of 1.2 until I get a stable version, and then I will update and continue updating with the main AC repository.

  This follows all the same licenses as AC does. My code isn't anything
special, so feel free to use what I added in anyway you want.


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
	