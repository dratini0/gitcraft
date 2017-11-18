#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gzip
import sys
from nbt_codec import NBTCodec

class GzipCodec(object):
    def __init__(self, encapsulated):
        self._encapsulated = encapsulated

    def process(self, in_file, out_file):
        decompressed = gzip.GzipFile(fileobj=in_file)
        out_file.write(b"GZIP\n")
        self._encapsulated.process(decompressed, out_file)

if __name__ == "__main__":
   GzipCodec(NBTCodec).process(open(sys.argv[1], "rb"), sys.stdout.buffer)
