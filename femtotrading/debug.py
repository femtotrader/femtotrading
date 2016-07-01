#!/usr/bin/env/python


def ensure_dt_increasing(dt_prev, dt):
    if dt_prev < dt:
        raise NotImplementedError("Time must be increasing dt_prev < dt with dt_prev=%s dt=%s" % (dt_prev, dt))
    return True
