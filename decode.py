from os import path, makedirs
from struct import unpack
from typing import BinaryIO
from zlib import crc32

from main import SIGNATURE


# struct packing directives:
#       B for unsigned char,       1 byte
#       H for unsigned short,      2 bytes
#       I for unsigned int,        4 bytes


def check_hashsum(archive: BinaryIO) -> bool:
    archive.seek(-4, 2)
    archive_checksum = unpack('I', archive.read(4))[0]
    archive.seek(0)
    new_checksum = crc32(archive.read()[:-4])
    archive.seek(0)

    if archive_checksum != new_checksum:
        print("Invalid checksum")
        return False

    return True


def check_signature(signature: bytes) -> bool:
    if signature != SIGNATURE:
        print("Invalid signature")
        return False

    return True


def read_starting_header_part(archive: BinaryIO) -> tuple[bytes, int, int, int, int]:
    signature = archive.read(8)
    version = unpack('B', archive.read(1))[0]
    algorithms_codes = unpack('B', archive.read(1))[0]
    extra_fields_amount = read_extra_fields_header_part(archive)  # placeholder to read 1 byte
    file_count = unpack('H', archive.read(2))[0]

    return signature, version, algorithms_codes, extra_fields_amount, file_count


def read_extra_fields_header_part(archive: BinaryIO) -> int:
    extra_fields_amount = unpack('B', archive.read(1))[0]

    for _ in range(extra_fields_amount):
        # some code in future
        ...

    return extra_fields_amount


def unpack_and_save_file(archive: BinaryIO, output_folder: str) -> None:
    relative_path_length = unpack('H', archive.read(2))[0]
    relative_path = archive.read(relative_path_length).decode('utf-8')
    file_size = unpack('Q', archive.read(4))[0]

    output_path = path.join(output_folder, relative_path)
    makedirs(path.dirname(output_path), exist_ok=True)

    with open(output_path, 'wb') as f:
        f.write(archive.read(file_size))


def decode(archive_path: str, output_folder: str) -> None:
    with open(archive_path, 'rb') as archive:
        if not check_hashsum(archive):
            return

        signature, _, _, _, file_count = read_starting_header_part(archive)

        if not check_signature(signature):
            return

        for _ in range(file_count):
            unpack_and_save_file(archive, output_folder)
