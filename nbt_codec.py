#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from collections import namedtuple
from struct import Struct
import base64
from common import handle_small_tag, handle_large_tag
ARRAY_LENGTH_STRUCT = Struct(">I")
STRING_LENGTH_STRUCT = Struct(">H")

Tag = namedtuple("Tag", ["id", "letter", "handler"])

def read_struct(struct, file):
    data = file.read(struct.size)
    if len(data) < struct.size:
        raise Exception("NBT file ends inside a value")
    return struct.unpack_from(data)

def TAG_Byte(nbt_file, output_file):
    handle_small_tag(nbt_file, output_file, 1)

def TAG_Short(nbt_file, output_file):
    handle_small_tag(nbt_file, output_file, 2)

def TAG_Int(nbt_file, output_file):
    handle_small_tag(nbt_file, output_file, 4)

def TAG_Long(nbt_file, output_file):
    handle_small_tag(nbt_file, output_file, 8)

def TAG_Float(nbt_file, output_file):
    handle_small_tag(nbt_file, output_file, 4)

def TAG_Double(nbt_file, output_file):
    handle_small_tag(nbt_file, output_file, 8)

def TAG_Byte_Array(nbt_file, output_file):
    size = read_struct(ARRAY_LENGTH_STRUCT, nbt_file)[0]
    handle_large_tag(nbt_file, output_file, size * 1)

def TAG_String(nbt_file, output_file):
    size = read_struct(STRING_LENGTH_STRUCT, nbt_file)[0]
    handle_small_tag(nbt_file, output_file, size * 1)

def TAG_List(nbt_file, output_file):
    tag = nbt_file.read(1)
    if tag == b'':
        raise Exception("NBT file ends before list type secification")
    size = read_struct(ARRAY_LENGTH_STRUCT, nbt_file)[0]
    if tag not in TAGS_BY_ID:
        raise Exception("Unknown tag: " + str(tag))
    output_file.write(TAGS_BY_ID[tag].letter)
    output_file.write(str(size).encode() + b"\n")
    for i in range(size):
        TAGS_BY_ID[tag].handler(nbt_file, output_file)

def TAG_Compound(nbt_file, output_file):
    NBTCodec.convert_tags(nbt_file, output_file, True)

def TAG_Int_Arrray(nbt_file, output_file):
    size = read_struct(ARRAY_LENGTH_STRUCT, nbt_file)[0]
    handle_large_tag(nbt_file, output_file, size * 4)

def TAG_Long_Array(nbt_file, output_file):
    size = read_struct(ARRAY_LENGTH_STRUCT, nbt_file)[0]
    handle_large_tag(nbt_file, output_file, size * 8)

TAGS = {
    Tag(b"\x00", b"}", None),
    Tag(b"\x01", b"b", TAG_Byte),
    Tag(b"\x02", b"h", TAG_Short),
    Tag(b"\x03", b"i", TAG_Int),
    Tag(b"\x04", b"l", TAG_Long),
    Tag(b"\x05", b"f", TAG_Float),
    Tag(b"\x06", b"d", TAG_Double),
    Tag(b"\x07", b"B", TAG_Byte_Array),
    Tag(b"\x08", b"s", TAG_String),
    Tag(b"\x09", b"[", TAG_List),
    Tag(b"\x0a", b"{", TAG_Compound),
    Tag(b"\x0b", b"I", TAG_Int_Arrray),
    Tag(b"\x0c", b"L", TAG_Long_Array),
}

TAGS_BY_ID = {tag.id: tag for tag in TAGS}

class NBTCodec(object):
    @staticmethod
    def convert_tags(nbt_file, output_file, is_compound = False):

        while True:
            tag = nbt_file.read(1)
            if tag == b"":
                if is_compound:
                    raise Exception("NBT file ends inside compund tag")
                else:
                    output_file.write(b"_NBT_END\n")
                    return
            if tag not in TAGS_BY_ID:
                raise Exception("Unknown tag: " + str(tag))
            output_file.write(TAGS_BY_ID[tag].letter)
            if tag == b"\0":
                if not is_compound:
                    raise Exception("TAG_End found outside of compound tag")
                else:
                    output_file.write(b"\n")
                    return
            TAG_String(nbt_file, output_file)
            TAGS_BY_ID[tag].handler(nbt_file, output_file)

    @classmethod
    def process(cls, in_file, out_file):
        out_file.write(b"NBT\n")
        cls.convert_tags(in_file, out_file, False)
    

if __name__ == "__main__":
    NBTCodec().process(open(sys.argv[1], "rb"), sys.stdout.buffer)
