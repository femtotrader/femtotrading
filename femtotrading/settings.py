#!/usr/bin/env/python

from __future__ import print_function

import os
import time
import warnings
import yaml
from munch import munchify, unmunchify
from .version import __name__


ENV_VAR_ROOT = __name__.upper()
DEFAULT_CONFIG_FILENAME = '~/%s.yml' % __name__.lower()


def from_env(key, default_value=None, root=ENV_VAR_ROOT):
    """Returns a value (url, login, password)
    using either default_value or using environment variable"""
    if root != "":
        ENV_VAR_KEY = root + "_" + key.upper()
    else:
        ENV_VAR_KEY = key.upper()
    if default_value == '' or default_value is None:
        try:
            return(os.environ[ENV_VAR_KEY])
        except:
            warnings.warn("You should pass %s using --%s or using environment variable %r" % (key, key, ENV_VAR_KEY))
            return(default_value)
    else:
        return(default_value)


DEFAULT = munchify({
    "CSV_DATA_DIR": from_env("CSV_DATA_DIR", "~/data/default_equities"),
    # "CSV_DATA_DIR": from_env("CSV_DATA_DIR", "~/data/default_fx"),
    "OUTPUT_DIR": from_env("OUTPUT_DIR", "~/%s" % __name__.lower())
})


TEST = munchify({
    "CSV_DATA_DIR": "data/default_equities",
    "OUTPUT_DIR": "out"
})


TEST_FX = munchify({
    "CSV_DATA_DIR": "data/default_fx",
    "OUTPUT_DIR": "out"
})


def from_file(fname=DEFAULT_CONFIG_FILENAME, testing=False):
    if testing:
        return TEST
    try:
        with open(os.path.expanduser(fname)) as fd:
            conf = yaml.load(fd)
        conf = munchify(conf)
        return conf
    except IOError:
        print("A configuration file named '%s' is missing" % fname)
        s_conf = yaml.dump(unmunchify(DEFAULT), explicit_start=True, indent=True, default_flow_style=False)
        print("""
Creating this file

%s

You still have to create directories with data and put your data in!
""" % s_conf)
        time.sleep(3)
        try:
            with open(os.path.expanduser(fname), "w") as fd:
                fd.write(s_conf)
        except IOError:
            print("Can create '%s'" % fname)
    print("Trying anyway with default configuration")
    return DEFAULT
