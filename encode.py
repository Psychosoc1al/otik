from os import path, walk
from struct import pack
from zlib import crc32

from constants import SIGNATURE, VERSION


# struct packing directives:
#       B for unsigned char,    1 byte
#       H for unsigned short,   2 bytes
#       I for unsigned int,     4 bytes


def check_input(file_paths: set[str]) -> bool:
    for file_path in file_paths:
        if not path.exists(file_path):
            print(f'Invalid file/folder path: {file_path}')
            return False

    return True


def create_starting_header_part(file_paths: set[tuple[str, str]]) -> bytes:
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


# divides folders into files, converts paths to relative
def preprocess_files_and_folders(file_paths: set[str]) -> set[tuple[str, str]]:
    preprocessed_file_paths = set()

    for file_path in file_paths:
        if path.isfile(file_path):
            preprocessed_file_paths.add(
                (path.basename(file_path), file_path)
            )

        elif path.isdir(file_path):
            base_folder = file_path.replace(path.basename(file_path), '')
            preprocessed_file_paths.add(
                (path.basename(file_path), path.join(base_folder, file_path))
            )
            for root, dirs, files in walk(file_path):
                print('root', root, 'dirs', dirs, 'files', files, 'base_folder', base_folder)
                for file in files:
                    full_path = path.join(root, file)
                    preprocessed_file_paths.add(
                        (path.relpath(full_path, base_folder), full_path)
                    )
                for ldir in dirs:
                    full_path = path.join(root, ldir)
                    preprocessed_file_paths.add(
                        (path.relpath(full_path, base_folder), full_path)
                    )

    return preprocessed_file_paths


def create_file_header_part(file_info: tuple[str, str]) -> bytes:
    relative_path, full_path = file_info
    relative_path = relative_path.encode('utf-8')
    relative_path_length = pack('H', len(relative_path))

    if path.isfile(full_path):
        original_file_size = pack('I', path.getsize(full_path))

        # file encoding function
        encoded_file_size = pack('I', path.getsize(full_path))

        with open(full_path, 'rb') as f:
            file_content = f.read()

        return relative_path_length + relative_path + original_file_size + encoded_file_size + file_content
    else:
        return relative_path_length + relative_path + pack('I', 1) + pack('I', 0) + b''


def encode(files_paths: set[str], archive_path: str) -> None:
    if not check_input(files_paths):
        return

    files_info = preprocess_files_and_folders(files_paths)

    with open(archive_path, 'a+b') as archive:
        starting_header_part = create_starting_header_part(files_info)
        archive.write(starting_header_part)

        for file_info in files_info:
            file_header_part = create_file_header_part(file_info)
            archive.write(file_header_part)

        archive.seek(0)
        checksum = pack('I', crc32(archive.read()))
        archive.write(checksum)
