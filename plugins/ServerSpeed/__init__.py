import acserver
from core.events import eventHandler

mpt_total = 0
mpt_last = 0
mpt_count = 0
mpt_millis = 0

def mpt_to_tps(mpt):
    return 1000.0/mpt

@eventHandler('serverExtension')
def serverext(cn,ext,ext_text):
    if ext == "tps":
        acserver.msg("Current: %d, Average: %f"%(mpt_to_tps(mpt_last),mpt_to_tps(float(mpt_total)/mpt_count)))

@eventHandler('serverTick')
def serverTick(gamemillis, servmillis):
    global mpt_total, mpt_count, mpt_last, mpt_millis
    if mpt_millis == -1:
        mpt_millis = servmillis
    else:
        diff = servmillis - mpt_millis
        mpt_total += diff
        mpt_count += 1
        mpt_last = diff
        mpt_millis = servmillis