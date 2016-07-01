#!/usr/bin/env/python

import time


def speed(ticks, t0):
    return ticks / (time.time() - t0)


def s_speed(time_event, ticks, t0):
    sp = speed(ticks, t0)
    s_typ = time_event.type.name
    return "%d %s processed @ %f %s/s" % (ticks, s_typ + "S", sp, s_typ)
