#!/usr/local/bin/python3
import getopt
import os
import sys
import xml.etree.ElementTree as ET
from sty import rs, fg, bg


def file_to_path(_file_name, _partitions):
    _directory = '/'
    for x in range(0, _partitions):
        _directory = _directory + _file_name[x] + '/'
    return _directory


def usage():
    print(rs.all + 'usage: move_wipedrive_xml.py -s <sourcePath> -o <outputPath> -p <partitions> [-f]')


def main():
    output_path = './tmp/'
    source_path = '.'
    partitions = 4
    force_overwrite = False
    success = 0
    failure = 0
    unknown = 0

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hfs:o:p:",
                                   ['help', 'force', 'sourcepath=', 'outputpath=', 'partitions='])
    except getopt.GetoptError as error:
        print(error)
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        elif opt in ('-f', '--force'):
            force_overwrite = True
        elif opt in ('-s', '--sourcepath'):
            source_path = arg.strip()
        elif opt in ('-o', '--outputpath'):
            output_path = arg.strip() + '/'
        elif opt in ('-p', '--partitions'):
            partitions = int(arg)

    for file in os.listdir(source_path):
        file_with_path = source_path + '/' + file
        if file_with_path.endswith('xml'):
            print('Processing ' + file_with_path)
            tree = ET.parse(file_with_path)
            job = tree.getroot().find('Report').find('Jobs').find('Job')
            size = job.find('Operation').find('Gigabytes').text

            output_directory = output_path + size + file_to_path(file, partitions)
            new_file = output_directory + file
            # print('Create `' + directory + '`')
            # print('Move `' + file + '` to `' +new_file +'`')
            print("\n+" + new_file, end='')
            print(' - ' + size + 'GB drives.')

            for Operation in job.findall('Operation'):
                gigabytes = Operation.find('Gigabytes').text
                drive_serial = Operation.find('Serial').text
                action_result = Operation.find('ActionResult').attrib['Index'].int()

                if action_result == 2:
                    result = fg.green + "Success"
                    success = success + 1
                elif action_result == 5:
                    result = bg.red + fg.li_white + "Failure"
                    failure = failure + 1
                else:
                    result = fg.cyan + "Unknown"
                    unknown = unknown + 1

                result = result + rs.all

                print("|--> " + drive_serial + ' - ' + gigabytes + "GB; Result: ", end='')
                print(result)

            try:
                os.makedirs(output_directory)
            except:
                pass
            file_exists = os.access(new_file, os.F_OK)
            if file_exists and force_overwrite is False:
                print(
                    fg.yellow + new_file + ' already exists and --force flag not sent. File not being output.' + rs.all)
            else:
                os.rename(file_with_path, new_file)

    print("\n\nFinished Processing Files.")
    total = success + failure + unknown
    print("Successful: " + success)
    print("Failed: " + failure)
    if unknown > 0:
        print("Unknown: " + unknown)
    print("Total: " + total)

if __name__ == "__main__":
    main()
