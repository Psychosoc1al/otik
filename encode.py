from os import path, walk
from struct import pack
from zlib import crc32

from constants import SIGNATURE, VERSION


# struct packing directives:
#       B for unsigned char,    1 byte
#       H for unsigned short,   2 bytes
#       I for unsigned int,     4 bytes


def check_input(targets: set[str]) -> bool:
    for target_path in targets:
        if not path.exists(target_path):
            print(f'Invalid target path: {target_path}')
            return False

    return True


def create_starting_header_part(targets: set[tuple[str, str]]) -> bytes:
    signature = SIGNATURE
    version = pack('B', VERSION)
    algorithms_codes = pack('B', 0)
    extra_fields_data = create_extra_fields_header_part()
    target_count = pack('H', len(targets))

    return signature + version + algorithms_codes + extra_fields_data + target_count


def create_extra_fields_header_part() -> bytes:
    extra_fields_amount = pack('B', 0)
    # some code in future

    return extra_fields_amount


# divides folders into files, converts paths to relative
def preprocess_targets(targets: set[str]) -> set[tuple[str, str]]:
    preprocessed_targets = set()

    for target in targets:
        if path.isfile(target):
            preprocessed_targets.add(
                (path.basename(target), target)
            )

        elif path.isdir(target):
            absolute_target_folder = path.abspath(target)
            target_parent_dir = path.dirname(absolute_target_folder)
            for root, dirs, files in walk(absolute_target_folder):
                for file in files:
                    absolute_target_file_path = path.join(root, file)
                    preprocessed_targets.add(
                        (path.relpath(absolute_target_file_path, target_parent_dir), absolute_target_file_path)
                    )
                preprocessed_targets.add(
                    (path.relpath(root, target_parent_dir) + path.sep, root)
                )

    return preprocessed_targets


def create_target_header_part(target_info: tuple[str, str]) -> bytes:
    relative_path, full_path = target_info
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


def encode(targets_paths: set[str], archive_path: str) -> None:
    if not check_input(targets_paths):
        return

    targets_info = preprocess_targets(targets_paths)

    with open(archive_path, 'a+b') as archive:
        starting_header_part = create_starting_header_part(targets_info)
        archive.write(starting_header_part)

        for target_info in targets_info:
            target_header_part = create_target_header_part(target_info)
            archive.write(target_header_part)

        archive.seek(0)
        checksum = pack('I', crc32(archive.read()))
        archive.write(checksum)
