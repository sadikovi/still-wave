#!/usr/bin/env python

# import libs
import os
import sys

# system paths
## file must be in project root
ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
LIB_PATH = os.path.join(ROOT_PATH, "lib")
LOCAL_PATH = os.path.join(ROOT_PATH, "local")

## set system path to the root directory
sys.path.append(ROOT_PATH)
## set system path to the lib
sys.path.append(LIB_PATH)
# set system path to the local
sys.path.append(LOCAL_PATH)
