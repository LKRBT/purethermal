#!/usr/bin/env python

from utils.get_cfg import get_cfg
from utils.viewhandler import ViewHandler

import os

if __name__ == '__main__':
  cfg = get_cfg()

  if not os.path.exists(cfg['PI']['FILE_PATH']):
    os.makedirs(cfg['PI']['FILE_PATH'])

  view = ViewHandler(cfg)
  view.run()
