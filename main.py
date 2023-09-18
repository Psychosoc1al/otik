from os import path, makedirs
from struct import pack, unpack
from zlib import crc32


# struct directives: H for unsigned short,      2 bytes
#                    I for unsigned int,        4 bytes
#                    Q for unsigned long long,  8 bytes

def create_starting_header_part(file_paths: list[str]) -> bytes:
    signature = b'PIN34MPR'
    version = pack('H', 1)
    algorithms_codes = pack('I', 0)
    file_count = pack('I', len(file_paths))

    return signature + version + algorithms_codes + file_count


def create_file_header_part(file_path: str) -> bytes:
    relative_path = file_path.encode('utf-8')
    rel_path_length = pack('H', len(relative_path))
    file_size = pack('Q', path.getsize(file_path))

    with open(file_path, 'rb') as f:
        file_content = f.read()

    return rel_path_length + relative_path + file_size + file_content


def encode(file_paths: list[str], archive_path: str) -> None:
    with open(archive_path, 'wb') as archive:
        starting_header_part = create_starting_header_part(file_paths)
        archive.write(starting_header_part)

        for file_path in file_paths:
            file_header_part = create_file_header_part(file_path)
            archive.write(file_header_part)

        checksum = pack('I', crc32(archive.read()))
        archive.write(checksum)


# Code below is not yet refactored

def decode(archive_path: str, output_folder: str) -> None:
    with open(archive_path, 'rb') as archive:
        signature = archive.read(8)
        if signature != b'PIN34MPR':
            print("Invalid signature")
            return

        # version = unpack('H', archive.read(2))[0]
        archive.read(2)
        # algorithms_codes = unpack('I', archive.read(4))[0]

        file_count = unpack('I', archive.read(4))[0]
        # header_checksum = unpack('I', archive.read(4))[0]
        archive.read(4)

        for _ in range(file_count):
            rel_path_length = unpack('H', archive.read(2))[0]
            rel_path = archive.read(rel_path_length).decode('utf-8')
            file_size = unpack('Q', archive.read(8))[0]

            output_path = path.join(output_folder, rel_path)
            makedirs(path.dirname(output_path), exist_ok=True)

            with open(output_path, 'wb') as f:
                f.write(archive.read(file_size))


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
