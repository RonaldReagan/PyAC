#include "cube.h"
#include "pyac_servermodule.h"

extern vector<client *> clients;

static PyObject *py_logline(PyObject *self, PyObject *args)
{
    char *s;
    int level = ACLOG_INFO;
    if(!PyArg_ParseTuple(args,  "s|i", &s, &level))
        return NULL;
    
    if (-1 < level && level < ACLOG_NUM) {
        logline(level,s);
    }
    
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *py_sendmsg(PyObject *self, PyObject *args) {
    char *msg;
    int cn = -1;
    if(!PyArg_ParseTuple(args,  "s|i", &msg,&cn))
        return NULL;
    
    sendservmsg(msg,cn);
    return Py_None;
}

static PyObject *py_getclient(PyObject *self, PyObject *args) {
    int cn;
    client *cl;

    if(!PyArg_ParseTuple(args,  "i", &cn)) return NULL;
    
    if (valid_client(cn)) {
        cl = clients[cn];
    }
    else {
        return Py_None;
    }

    int millis = servmillis - cl->connectmillis;
    //                 //  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21     22 23 24 25 26
    return Py_BuildValue("{si,ss,ss,si,si,si,si,si,si,si,si,si,si,si,si,si,si,si,si,si,s(fff),si,si,si,si,si}",
                         "cn",cl->clientnum,                     // 1
                         "hostname",cl->hostname,                // 2
                         "name",cl->name,                        // 3
                         "ping",cl->ping,                        // 4
                         "role",cl->role,                        // 5
                         "version",cl->acversion,                // 6
                         "buildtype",cl->acbuildtype,            // 7
                         "vote",cl->vote,                        // 8
                         "millis",millis,                        // 9
                         "frags",cl->state.frags,                // 10
                         "flags",cl->state.flagscore,            // 11
                         "scoped",cl->state.scoped?1:0,          // 12
                         "akimbomillis",cl->state.akimbomillis,  // 13
                         "teamkills",cl->state.teamkills,        // 14
                         "shotdamage",cl->state.shotdamage,      // 15
                         "damage",cl->state.damage,              // 16
                         "deaths",cl->state.deaths,              // 17
                         "points",cl->state.points,              // 18
                         "lastshot",cl->state.lastshot,          // 19
                         "state",cl->state.state,                // 20
                         "pos",cl->state.o.x,cl->state.o.x, cl->state.o.y,        // 21
                         "health",cl->state.health,              // 22
                         "armour",cl->state.armour,              // 23
                         "primary",cl->state.primary,            // 24
                         "nextprimary",cl->state.nextprimary,    // 25
                         "gunselect",cl->state.gunselect         // 26
                         );
}

static PyObject *py_killclient(PyObject *self, PyObject *args) {
    int tcn,acn,gib,weap ;
    if(!PyArg_ParseTuple(args,  "ii|i",&acn,&tcn,&gib,&weap )) return NULL;
    
    if(!valid_client(tcn)) return Py_None;
    if(!valid_client(acn)) return Py_None ;
    
    sendf(-1, 1, "ri5", gib ? SV_GIBDIED : SV_DIED, tcn, acn, clients[tcn]->state.frags, weap);
    
    return Py_None;
}

static PyObject *py_spawnclient(PyObject *self, PyObject *args) {
    int tcn,health,armour=-1,ammo=-1,mag=-1,weapon=-1,primaryweapon=-1;
    
    if(!PyArg_ParseTuple(args,  "ii|iiiii",&tcn, &health, &armour, &ammo, &mag, &weapon, &primaryweapon)) return NULL;
    
    if(!valid_client(tcn)) return Py_None;
    if(team_isspect(clients[tcn]->team)) return Py_None;
    clientstate &gs = clients[tcn]->state;

    if(armour==-1) armour = 0;
    if(primaryweapon == -1) primaryweapon = gs.primary;

    gs.respawn();
    gs.spawnstate(smode);
    gs.lifesequence++;
    if (ammo != -1) {
        gs.ammo[primaryweapon] = ammo;
    }
    if (mag != -1) {
        gs.mag[primaryweapon] = mag;
    }
    if(primaryweapon != -1 || !(primaryweapon >= 0 && primaryweapon < NUMGUNS)) {
        gs.primary = gs.nextprimary = primaryweapon;
    }
    if(weapon != -1 || !(weapon >= 0 && weapon < NUMGUNS)) {
        gs.gunselect = weapon;
    }
    gs.health = health;
    gs.armour = armour;

    sendf(tcn, 1, "ri7vv", SV_SPAWNSTATE, gs.lifesequence, gs.health, gs.armour, gs.primary,
        gs.gunselect, m_arena ? clients[tcn]->spawnindex : -1, NUMGUNS, gs.ammo, NUMGUNS, gs.mag);
    gs.lastspawn = gamemillis;
    return Py_None;
}

static PyObject *py_getcommandline(PyObject *self) {
    #define PY_SCL(name) #name,scl.name
    #define PY_SCL_B(name) #name,scl.name ? 1:0
    //                 //  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39
    return Py_BuildValue("{si,si,si,si,si,si,si,si,si,si,si,si,si,si,ss,ss,ss,ss,ss,ss,ss,ss,ss,ss,ss,ss,ss,ss,ss,ss,ss,si,si,si,ss,ss,ss,ss,ss}",
                         PY_SCL(uprate),                      // 1
                         PY_SCL(serverport),                  // 2
                         PY_SCL(syslogfacility),              // 3
                         PY_SCL(filethres),                   // 4
                         PY_SCL(syslogthres),                 // 5
                         PY_SCL(maxdemos),                    // 6
                         PY_SCL(maxclients),                  // 7
                         PY_SCL(kickthreshold),               // 8
                         PY_SCL(banthreshold),                // 9
                         PY_SCL(verbose),                     // 10
                         PY_SCL(incoming_limit),              // 11
                         PY_SCL(afk_limit),                   // 12
                         PY_SCL(ban_time),                    // 13
                         PY_SCL(demotimelocal),               // 14
                         
                         PY_SCL(ip),                          // 15
                         PY_SCL(master),                      // 16
                         PY_SCL(logident),                    // 17
                         PY_SCL(serverpassword),              // 18
                         PY_SCL(adminpasswd),                 // 19
                         PY_SCL(demopath),                    // 20
                         PY_SCL(maprot),                      // 21
                         PY_SCL(pwdfile),                     // 22
                         PY_SCL(blfile),                      // 23
                         PY_SCL(nbfile),                      // 24
                         PY_SCL(infopath),                    // 25
                         PY_SCL(motdpath),                    // 26
                         PY_SCL(forbidden),                   // 27
                         PY_SCL(killmessages),                // 28
                         PY_SCL(demofilenameformat),          // 29
                         PY_SCL(demotimestampformat),         // 30
                         PY_SCL(py_global_config),            // 31
                         
                         PY_SCL_B(logtimestamp),              // 32
                         PY_SCL_B(demo_interm),               // 33
                         PY_SCL_B(loggamestatus),             // 34
                         
                         PY_SCL(motd),                        // 35
                         PY_SCL(servdesc_full),               // 36
                         PY_SCL(servdesc_pre),                // 37
                         PY_SCL(servdesc_suf),                // 38
                         PY_SCL(voteperm)                     // 39
                         );
    #undef PY_SCL
    #undef PY_SCL_B
}

static PyObject *py_getadminpasswords(PyObject *self) {
    PyObject *retTuple;
    
    if (!passwords.adminpwds.length()) return Py_None;
    
    retTuple = PyTuple_New(passwords.adminpwds.length());
    loopv(passwords.adminpwds)
    {
        PyObject *tmpTuple = Py_BuildValue("sii",passwords.adminpwds[i].pwd,passwords.adminpwds[i].line,passwords.adminpwds[i].denyadmin ? 1:0);
        PyTuple_SetItem(retTuple, i, tmpTuple);
    }
    return retTuple; 
}

static PyObject *py_setgamelimit(PyObject *self, PyObject *args) {
    int timeoffset;
    
    if(!PyArg_ParseTuple(args,  "i",&timeoffset)) return NULL;
    
    gamelimit = timeoffset;
    checkintermission();
    
    return PyInt_FromLong(gamelimit);
}

static PyObject *py_getgamelimit(PyObject *self) {
    return PyInt_FromLong(gamelimit);
}

static PyObject *py_getgamemillis(PyObject *self) {
    return PyInt_FromLong(gamelimit);
}

static PyObject *py_getminremain(PyObject *self) {
    return PyInt_FromLong(minremain);
}

static PyObject *py_getservmillis(PyObject *self) {
    return PyInt_FromLong(servmillis);
}

static PyMethodDef ModuleMethods[] = {
	{"log", py_logline, METH_VARARGS, "Logs a message."},
    {"msg", py_sendmsg, METH_VARARGS, "Sends a server message."},
    {"getClient", py_getclient, METH_VARARGS, "Gets a client dictionary."},
    {"killClient", py_killclient, METH_VARARGS, "Kills a acn as if tcn killed them."},
    {"spawnClient", py_spawnclient, METH_VARARGS, "Spawns cn with specified stats"},
    {"getCmdLineOptions", (PyCFunction)py_getcommandline, METH_NOARGS, "Retrieves a dictionary of all of the commandline options."},
    {"getAdminPasswords", (PyCFunction)py_getadminpasswords, METH_NOARGS, "Retrieves a tuple of all of the passwords."},
    {"setGameLimit", py_setgamelimit, METH_VARARGS, "Sets the time limit for the game."},
    {"getGameLimit", (PyCFunction)py_getgamelimit, METH_NOARGS, "Gets the time limit for the game."},
    {"getGameMillis", (PyCFunction)py_getgamemillis, METH_NOARGS, "Gets the time spent in the game."},
    {"getMinRemain", (PyCFunction)py_getminremain, METH_NOARGS, "Gets the number of minutes remaining."},
    {"getServMillis", (PyCFunction)py_getservmillis, METH_NOARGS, "Gets the number of milliseconds that the server has been running."},
	{NULL, NULL, 0, NULL},
};

PyMODINIT_FUNC
initModule()
{
	(void) Py_InitModule("acserver", ModuleMethods);
	return;
}