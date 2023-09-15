import os
import struct


def create_header(file_path):
    rel_path = file_path.encode('utf-8')
    rel_path_length = struct.pack('H', len(rel_path))
    file_size = struct.pack('Q', os.path.getsize(file_path))
    return rel_path_length + rel_path + file_size


def encode(file_paths, archive_path):
    signature = b'PIN34MPR'
    version = struct.pack('H', 1)
    algo_codes = struct.pack('I', 0)
    file_count = struct.pack('I', len(file_paths))

    header_checksum = struct.pack('I', 0)  # Placeholder for checksum
    header = signature + version + algo_codes + file_count + header_checksum

    with open(archive_path, 'wb') as archive:
        archive.write(header)

        for path in file_paths:
            file_header = create_header(path)
            archive.write(file_header)

            with open(path, 'rb') as f:
                archive.write(f.read())


def decode(archive_path, output_folder):
    with open(archive_path, 'rb') as archive:
        signature = archive.read(8)
        if signature != b'PIN34MPR':
            print("Invalid signature")
            return

        # version = struct.unpack('H', archive.read(2))[0]
        archive.read(2)
        algo_codes = struct.unpack('I', archive.read(4))[0]

        if algo_codes != 0:
            print("Unsupported algorithm codes")
            return

        file_count = struct.unpack('I', archive.read(4))[0]
        # header_checksum = struct.unpack('I', archive.read(4))[0]
        archive.read(4)

        for _ in range(file_count):
            rel_path_length = struct.unpack('H', archive.read(2))[0]
            rel_path = archive.read(rel_path_length).decode('utf-8')
            file_size = struct.unpack('Q', archive.read(8))[0]

            output_path = os.path.join(output_folder, rel_path)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, 'wb') as f:
                f.write(archive.read(file_size))


if __name__ == '__main__':
    action = input("Encode or Decode? (e/d): ")
    if action == 'e':
        file_paths_arg = input("Enter file paths separated by comma: ").split(',')
        archive_path_arg = input("Enter archive path: ")
        encode(file_paths_arg, archive_path_arg)
    elif action == 'd':
        archive_path_arg = input("Enter archive path: ")
        output_folder_arg = input("Enter output folder: ")
        decode(archive_path_arg, output_folder_arg)
