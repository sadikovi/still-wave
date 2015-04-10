#!/usr/bin/env python

from types import UnicodeType
import json
import urllib2
import uuid
import urlparse

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

def getShareUrlId(shareUrl):
    pieces = shareUrl.split("/")
    return pieces[-1] if len(pieces) > 0 else None

def getUrlPath(url):
    a = urlparse.urlparse(url)
    return a.path if a else ""

def unquoteParam(param):
    raw = str(param).strip()
    return urllib2.unquote(raw)

def quoteParam(param):
    return urllib2.quote(param)

def toInt(value):
    res = None
    try:
        res = int(value)
    except (ValueError, TypeError):
        res = None
    finally:
        return res

def toUnsignedInt(value):
    res = toInt(value)
    return res*(-1) if res and res < 0 else res

def ceilDivison(x, y):
    return x/y + (0 if x%y == 0 else 1)

def pages(current, max, frame):
    if current < 1: current = 1
    if max < 1: max = 1
    if frame < 1: frame = 1
    if current > max: current = max
    if frame >= max: frame = max-1
    left = current - frame / 2
    right = current + frame / 2
    dl = left - 1 if left < 1 else 0
    dr = right-max if right > max else 0
    a = range(left-dl, right-dr+1)
    a = range(a[0]-dr, a[-1]-dl+1)
    return a

def newId():
    return uuid.uuid4().hex

def toBool(value):
    if value in ["0", "False", "false"]:
        value = False
    return bool(value)
