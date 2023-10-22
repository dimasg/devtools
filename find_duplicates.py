#!/usr/bin/env python3
""" find duplicate files """

import argparse
import logging
import os


def find_duplicates(cmd_args):
    """ find duplicates """
    files_info = {}

    for root, dirs, files in os.walk(cmd_args.dir, topdown=True):
        logging.debug('Walking ... %s, %s, %s', root, dirs, files)
        for next_dir in cmd_args.ignore_dir:
            if next_dir in dirs:
                logging.debug('%s will be skipped', next_dir)
                dirs.remove(next_dir)

        for file_name in files:
            file_path = os.path.join(root, file_name)
            stats = os.stat(file_path)
            logging.debug('File %s stats %s', file_path, stats)
            file_info = {'path': root, 'size': stats.st_size}
            if file_name in files_info:
                files_info[file_name].append(file_info)
            else:
                files_info[file_name] = [file_info]

    logging.debug('Files:\n%s', files_info)

    print(f'Found files: {len(files_info.keys())}')
    print('Duplicates found:')

    for file_name, infos in files_info.items():
        if len(infos) < 2:
            continue
        print(f'File {file_name} found in:'.format(file_name))
        for info in infos:
            print(f"\tsize: {info['size']}, path: {info['path']}")


def main():
    """ main subroutine """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'dir', action='store',
        help='directory to find'
    )
    parser.add_argument(
        '--ignore-dir', action='store',
        nargs='*', default=[],
        help='ignore one or more dirs'
    )
    parser.add_argument(
        '--debug', action='store_const',
        const=logging.DEBUG, default=logging.ERROR,
        help='debug output'
    )
    parser.add_argument(
        '--info', action='store_const', dest='debug',
        const=logging.INFO, default=logging.ERROR,
        help='info output'
    )
    cmd_args = parser.parse_args()

    logging.basicConfig(
        level=cmd_args.debug,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.debug('Parsed command line args: %s', cmd_args)

    find_duplicates(cmd_args)


if __name__ == "__main__":
    main()

# vim: ts=4 sw=4
