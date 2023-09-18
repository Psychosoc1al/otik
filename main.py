from os import path, makedirs
from struct import pack, unpack
from typing import BinaryIO
from zlib import crc32

# struct packing directives:
#       B for unsigned char,       1 byte
#       H for unsigned short,      2 bytes
#       I for unsigned int,        4 bytes

SIGNATURE = b'PIN34MPR'


# Encoding part

def create_starting_header_part(file_paths: list[str]) -> bytes:
    signature = SIGNATURE
    version = pack('B', 1)
    algorithms_codes = pack('B', 0)
    extra_fields_data = create_extra_fields_header_part()
    file_count = pack('H', len(file_paths))

    return signature + version + algorithms_codes + extra_fields_data + file_count


def create_extra_fields_header_part() -> bytes:
    extra_fields_amount = pack('H', 0)
    # some code in future

    return extra_fields_amount


def create_file_header_part(file_path: str) -> bytes:
    relative_path = file_path.encode('utf-8')
    relative_path_length = pack('H', len(relative_path))
    file_size = pack('Q', path.getsize(file_path))

    with open(file_path, 'rb') as f:
        file_content = f.read()

    return relative_path_length + relative_path + file_size + file_content


def encode(file_paths: list[str], archive_path: str) -> None:
    with open(archive_path, 'wb') as archive:
        starting_header_part = create_starting_header_part(file_paths)
        archive.write(starting_header_part)

        for file_path in file_paths:
            file_header_part = create_file_header_part(file_path)
            archive.write(file_header_part)

        checksum = pack('I', crc32(archive.read()))
        archive.write(checksum)


# Decoding part

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


if __name__ == '__main__':
    action = input("Encode or Decode? (e/d): ")

    if action == 'e':
        file_paths_arg = input("Enter file [full or relative] paths separated by vertical bar (|): ").split('|')
        archive_path_arg = input("Enter archive [full or relative] path: ")
        encode(file_paths_arg, archive_path_arg)
    elif action == 'd':
        archive_path_arg = input("Enter archive [full or relative] path: ")
        output_folder_arg = input("Enter output folder [full or relative] path: ")
        decode(archive_path_arg, output_folder_arg)
