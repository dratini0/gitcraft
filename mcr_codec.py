#!/usr/bin/env python3

import sys, os, zlib, gzip
import common
from struct import Struct
from io import BytesIO
from nbt_codec import NBTCodec
from raw_codec import RawCodec

OFFSET_STRUCT = Struct("!bhb")
CHUNK_COUNT = 32 * 32
OFFSETS_SIZE = OFFSET_STRUCT.size * CHUNK_COUNT
TIMESTAMPS_OFFSET = OFFSETS_SIZE
TIMESTAMPS_SIZE = 4 * CHUNK_COUNT
PACKING_STRUCT = Struct("!ib")
class MCRCodec(object):
    def __init__(self, encapsulated):
        self._encapsulated = encapsulated

    def process(self, mcr_file, out_file):
        out_file.write(b"MCR\n")
        offsets = mcr_file.read(OFFSETS_SIZE)
        if len(offsets) < OFFSETS_SIZE:
            raise Exception("Region file ends inside offsets")

        mcr_file.seek(TIMESTAMPS_OFFSET)
        common.handle_large_tag(mcr_file, out_file, TIMESTAMPS_SIZE)

        for index in range(CHUNK_COUNT):
            struct_offset = OFFSET_STRUCT.unpack_from(offsets, OFFSET_STRUCT.size * index)
            if struct_offset == (0, 0, 0):
                out_file.write(b"EMPTY\n")
            else:
                mcr_file.seek(struct_offset[0] << 24 | struct_offset[1] << 12)
                chunk_packed = mcr_file.read(struct_offset[2] << 12)

                chunk_packing = PACKING_STRUCT.unpack_from(chunk_packed)
                chunk_zipped = chunk_packed[PACKING_STRUCT.size:chunk_packing[0] + PACKING_STRUCT.size - 1]
                if chunk_packing[1] == 1:
                    chunk = gzip.decompress(chunk_zipped)
                elif chunk_packing[1] == 2:
                    chunk = zlib.decompress(chunk_zipped)
                else:
                    raise Exception("Undefined compression method " + 
                                    str(chunk_packing[1]))

                self._encapsulated.process(BytesIO(chunk), out_file)

if __name__ == "__main__":
    MCRCodec(NBTCodec()).process(open(sys.argv[1], "rb"), sys.stdout.buffer)
