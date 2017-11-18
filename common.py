import base64

def handle_small_tag(nbt_file, output_file, size):
    payload = nbt_file.read(size)
    if len(payload) < size:
        raise Exception("NBT file ends inside a tag payload")
    output_file.write(base64.b64encode(payload))
    output_file.write(b"\n")

def handle_large_tag(nbt_file, output_file, size):
    while size > 64:
        handle_small_tag(nbt_file, output_file, 64)
        size -= 64
    handle_small_tag(nbt_file, output_file, size)
    output_file.write(b"=\n")

