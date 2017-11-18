#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gzip
import os
import os.path
import re
import sys

from raw_codec import RawCodec
from gzip_codec import GzipCodec
from nbt_codec import NBTCodec
from mcr_codec import MCRCodec

BLACKLIST = [
    "##MCEDIT.TEMP##",
    ".*/##MCEDIT.TEMP##"
]

def probeMCR(filename):
    return filename.endswith(".mca") or filename.endswith(".mcr")

def probeGzipNBT(filename):
    try:
        with gzip.open(filename, "rb") as f:
            return f.read(3) == b"\x0a\x00\x00"
    except:
        return False

def probeRawNBT(filename):
    with open(filename, "rb") as f:
        return f.read(3) == b"\x0a\x00\x00"

def probeMiscGzip(filename):
    with open(filename, "rb") as f:
        return f.read(2) == b"\x1f\x8b"

def probeBlacklist(filename):
    return any(map(lambda pattern: re.match(pattern, filename) is not None, BLACKLIST))

CODECS = [
    (probeMCR, MCRCodec(NBTCodec())),
    (probeGzipNBT, GzipCodec(NBTCodec())),
    (probeRawNBT, NBTCodec()),
    (probeMiscGzip, GzipCodec(RawCodec())),
]

def main(world_dir, out_dir):
    for path, dirs, files in os.walk(world_dir):
        real_path = path[len(world_dir) + 1:]
        print(repr(real_path))
        print(dirs)
        print(files)
        not_blacklisted = []
        for dirname in dirs:
            real_dir = os.path.join(real_path, dirname)
            if not probeBlacklist(real_dir):
                not_blacklisted.append(dirname)
                os.makedirs(os.path.join(out_dir, real_dir), exist_ok=True)
        dirs.clear()
        dirs.extend(not_blacklisted)
        for filename in files:
            real_file = os.path.join(real_path, filename)
            if probeBlacklist(real_file):
                continue
            codec = next((codec for test, codec in CODECS if test(os.path.join(path, filename))), RawCodec)
            with open(os.path.join(out_dir, real_file), "wb") as out_handle:
                with open(os.path.join(path, filename), mode="rb") as in_handle:
                    codec.process(in_handle, out_handle)
            

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
