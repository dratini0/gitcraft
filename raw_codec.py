class RawCodec(object):
    @staticmethod
    def process(in_file, out_file):
        out_file.write(b"RAW\n")
        in_file = in_file.read()
        out_file.write(str(len(in_file)).encode() + b"\n")
        out_file.write(in_file)
