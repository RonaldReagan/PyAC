extern void sendservmsg(const char *msg, int cn);
extern void sendf(int cn, int chan, const char *format, ...);
extern void checkintermission();

extern int servmillis, gamemillis, gamelimit, minremain;

extern struct servercommandline scl;

struct pwddetail
{
    string pwd;
    int line;
    bool denyadmin;    // true: connect only
};

struct serverpasswords : serverconfigfile
{
    vector<pwddetail> adminpwds;
    int staticpasses;
};

#define CONFIG_MAXPAR 6

struct configset
{
    string mapname;
    union
    {
        struct { int mode, time, vote, minplayer, maxplayer, skiplines; };
        int par[CONFIG_MAXPAR];
    };
};

struct servermaprot : serverconfigfile
{
    vector<configset> configsets;
    int curcfgset;
};

extern serverpasswords passwords;
extern servermaprot maprot;