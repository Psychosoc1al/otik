from decode import decode
from encode import encode

SIGNATURE = b'PIN34MPR'

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
