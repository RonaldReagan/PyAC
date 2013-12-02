extern void sendservmsg(const char *msg, int cn);
extern void sendf(int cn, int chan, const char *format, ...);
static int gamemillis;
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

extern serverpasswords passwords;