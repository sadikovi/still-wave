#!/usr/bin/env python

from types import UnicodeType
import json
import urllib2

def _decode_dict(data):
    for key in data.keys():
        key_upd = key; data_upd = data[key]
        if type(key_upd) is UnicodeType:
            key_upd = str(key_upd.encode('ascii','replace'))
        if type(data_upd) is UnicodeType:
            data_upd = str(data_upd.encode('ascii','replace'))
        del data[key]
        data[key_upd] = data_upd
    return data

def toJson(str, decode=_decode_dict):
    # parse json
    return json.loads(str, object_hook=decode)

def getSharUrlId(shareUrl):
    pieces = shareUrl.split("/")
    return pieces[-1] if len(pieces) > 0 else None

def unquoteParam(param):
    raw = str(param).strip()
    return urllib2.unquote(raw)
