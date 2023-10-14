from os import path, makedirs
from struct import unpack
from typing import BinaryIO
from zlib import crc32

from constants import SIGNATURE


# struct packing directives:
#       B for unsigned char,    1 byte
#       H for unsigned short,   2 bytes
#       I for unsigned int,     4 bytes


def check_input(archive_path: str) -> bool:
    if not path.exists(archive_path):
        print(f'Invalid archive path: {archive_path}')
        return False

    return True


def check_hashsum(archive: BinaryIO) -> bool:
    archive.seek(-4, 2)
    archive_checksum = unpack('I', archive.read(4))[0]
    archive.seek(0)
    new_checksum = crc32(archive.read()[:-4])
    archive.seek(8)

    if archive_checksum != new_checksum:
        print('Invalid checksum')
        return False

    return True


def check_signature(archive: BinaryIO) -> bool:
    signature = archive.read(8)
    if signature != SIGNATURE:
        print('Invalid signature')
        return False

    return True


def check_algorithms_codes(algorithms_codes: int, allowed_algorithms_codes: int) -> bool:
    # allowed_algorithms_codes is an integer with binary like 00011001 which is concatenated of algorithms codes:
    # algorithm X is 0001 and algorithm Y is 1001 which gives 00011001
    if algorithms_codes != allowed_algorithms_codes:
        print('Invalid algorithms codes')
        return False

    return True


def read_starting_header_part(archive: BinaryIO) -> tuple[int, int, int, int]:
    version = unpack('B', archive.read(1))[0]
    algorithms_codes = unpack('B', archive.read(1))[0]
    extra_fields_amount = read_extra_fields_header_part(archive)  # placeholder to read 1 byte
    file_count = unpack('H', archive.read(2))[0]

    return version, algorithms_codes, extra_fields_amount, file_count


def read_extra_fields_header_part(archive: BinaryIO) -> int:
    extra_fields_amount = unpack('B', archive.read(1))[0]

    for _ in range(extra_fields_amount):
        # some code in future
        ...

    return extra_fields_amount


def unpack_and_save_file(archive: BinaryIO, output_folder: str) -> None:
    relative_path_length = unpack('H', archive.read(2))[0]
    relative_path = archive.read(relative_path_length).decode('utf-8')
    original_file_size = unpack('I', archive.read(4))[0]
    encoded_file_size = unpack('I', archive.read(4))[0]
    if original_file_size + encoded_file_size == 1:
        relative_path += '/'

    output_path = path.join(output_folder, relative_path)
    makedirs(path.dirname(output_path), exist_ok=True)

    if original_file_size + encoded_file_size != 1:
        with open(output_path, 'wb') as f:
            # file decoding function
            f.write(archive.read(encoded_file_size))


def decode(archive_path: str, output_folder: str) -> None:
    if not check_input(archive_path):
        return

    with open(archive_path, 'rb') as archive:
        if not check_signature(archive):
            return

        if not check_hashsum(archive):
            return

        _, algorithms_codes, _, file_count = read_starting_header_part(archive)

        if not check_algorithms_codes(algorithms_codes, 0):
            return

        for _ in range(file_count):
            unpack_and_save_file(archive, output_folder)
