from os import path, makedirs
from struct import pack, unpack
from typing import BinaryIO
from zlib import crc32


# struct directives: H for unsigned short,      2 bytes
#                    I for unsigned int,        4 bytes
#                    Q for unsigned long long,  8 bytes

# Encoding part

def create_starting_header_part(file_paths: list[str]) -> bytes:
    signature = b'PIN34MPR'
    version = pack('H', 1)
    algorithms_codes = pack('I', 0)
    file_count = pack('I', len(file_paths))

    return signature + version + algorithms_codes + file_count


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

def check_checksum(archive_path: str) -> bool:
    with open(archive_path, 'rb') as archive:
        archive_content = archive.read()
        archive_checksum = unpack('I', archive_content[-4:])[0]
        new_checksum = crc32(archive_content[:-4])

        if archive_checksum != new_checksum:
            print("Invalid checksum")
            return False

        return True


def check_signature(signature: bytes) -> bool:
    if signature != b'PIN34MPR':
        print("Invalid signature")
        return False

    return True


def read_starting_header_part(archive: BinaryIO) -> tuple[bytes, int, int, int]:
    signature = archive.read(8)
    version = unpack('H', archive.read(2))[0]
    algorithms_codes = unpack('I', archive.read(4))[0]
    file_count = unpack('I', archive.read(4))[0]

    return signature, version, algorithms_codes, file_count


def unpack_and_save_file(archive: BinaryIO, output_folder: str) -> None:
    relative_path_length = unpack('H', archive.read(2))[0]
    relative_path = archive.read(relative_path_length).decode('utf-8')
    file_size = unpack('Q', archive.read(8))[0]

    output_path = path.join(output_folder, relative_path)
    makedirs(path.dirname(output_path), exist_ok=True)

    with open(output_path, 'wb') as f:
        f.write(archive.read(file_size))


def decode(archive_path: str, output_folder: str) -> None:
    if not check_checksum(archive_path):
        return

    with open(archive_path, 'rb') as archive:
        signature, _, _, file_count = read_starting_header_part(archive)

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
