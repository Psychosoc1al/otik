from decode import decode
from encode import encode


if __name__ == '__main__':
    action = input('Encode or Decode? (e/d): ')

    if action in 'eу':
        files_paths = set(input('Enter targets [full or relative] paths separated by vertical bar (|): ').split('|'))
        archive_path = input('Enter archive [full or relative] path: ')
        encode(files_paths, archive_path)
    elif action in 'dв':
        archive_path = input('Enter archive [full or relative] path: ')
        output_folder = input('Enter output folder [full or relative] path: ')
        decode(archive_path, output_folder)
