#!/usr/bin/python3
import getopt
import os
import sys
import xml.etree.ElementTree as ET


def file_to_path(_file_name, _partitions):
    _directory = '/'
    for x in range(0, _partitions):
        _directory = _directory + _file_name[x] + '/'
    return _directory


def usage():
    print('usage: move_wipedrive_xml.py -s <sourcePath> -o <outputPath> -p <partitions> [-f]')


def main():
    regular_text = '\033[1;m'
    success_text = '\033[1;32m'
    error_text = '\033[1;41m'
    info_text = '\033[1;33m'
    result_color = {'2': success_text,
                    '5': error_text
                    }
    output_path = './tmp/'
    source_path = '.'
    partitions = 4
    force_overwrite = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hfs:o:p:", ['help', 'force', 'sourcepath=', 'outputpath=', 'partitions='])
    except getopt.GetoptError as error:
        print(error)
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in('-h', '--help'):
            usage()
            sys.exit()
        elif opt in('-f', '--force'):
            force_overwrite = True
        elif opt in ('-s', '--sourcepath'):
            source_path = arg.strip()
        elif opt in('-o', '--outputpath'):
            output_path = arg.strip() + '/'
        elif opt in('-p', '--partitions'):
            partitions = int(arg)

    for file in os.listdir(source_path):
        file_with_path = source_path + '/' + file
        if file_with_path.endswith('xml'):
            print('Processing ' + file_with_path)
            tree = ET.parse(file_with_path)
            reports = tree.getroot()
            job = reports.find('Report').find('Jobs').find('Job')
            size = job.find('Operation').find('Gigabytes').text
            output_directory = file_to_path(file, partitions)
            output_directory = output_path + size + output_directory
            new_file = output_directory + file
            # print('Create `' + directory + '`')
            # print('Move `' + file + '` to `' +newfile +'`')
            print("\n+" + new_file, end='')
            print(' - ' + size + 'GB drives.')
            for Operation in job.findall('Operation'):
                gigabytes = Operation.find('Gigabytes')
                drive_serial = Operation.find('Serial')
                action_result = Operation.find('ActionResult')
                result = "Success" if (action_result.attrib['Index'] == '2') else "Failure"

                print("|--> " + drive_serial.text + ' - ' + gigabytes.text + "GB; Result: ", end='')
                print (result_color.get(action_result.attrib['Index'], info_text) + result + regular_text)

            try:
                os.makedirs(output_directory)
            except:
                pass
            os.rename(file_with_path, new_file) # todo: check for force_overwrite

    print("\n\nFinished Processing Files.")


if __name__ == "__main__":
    main()
