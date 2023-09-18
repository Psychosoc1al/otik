from os import path
from struct import pack
from zlib import crc32

from constants import SIGNATURE, VERSION


# struct packing directives:
#       B for unsigned char,    1 byte
#       H for unsigned short,   2 bytes
#       I for unsigned int,     4 bytes


def create_starting_header_part(file_paths: list[str]) -> bytes:
    signature = SIGNATURE
    version = pack('B', VERSION)
    algorithms_codes = pack('B', 0)
    extra_fields_data = create_extra_fields_header_part()
    file_count = pack('H', len(file_paths))

    return signature + version + algorithms_codes + extra_fields_data + file_count


def create_extra_fields_header_part() -> bytes:
    extra_fields_amount = pack('B', 0)
    # some code in future

    return extra_fields_amount


def create_file_header_part(file_path: str) -> bytes:
    relative_path = file_path.encode('utf-8')
    relative_path_length = pack('H', len(relative_path))
    file_size = pack('I', path.getsize(file_path))

    with open(file_path, 'rb') as f:
        file_content = f.read()

    return relative_path_length + relative_path + file_size + file_content


def encode(file_paths: list[str], archive_path: str) -> None:
    with open(archive_path, 'a+b') as archive:
        starting_header_part = create_starting_header_part(file_paths)
        archive.write(starting_header_part)

        for file_path in file_paths:
            file_header_part = create_file_header_part(file_path)
            archive.write(file_header_part)

        archive.seek(0)
        checksum = pack('I', crc32(archive.read()))
        archive.write(checksum)
