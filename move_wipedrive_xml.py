#!/usr/local/bin/python3
import getopt
import os
import sys
import xml.etree.ElementTree as ET
import sty


def file_to_path(_file_name, _partitions):
    _directory = '/'
    for x in range(0, _partitions):
        _directory = _directory + _file_name[x] + '/'
    return _directory


def usage():
    print(sty.rs.all + 'usage: move_wipedrive_xml.py -s <sourcePath> -o <outputPath> -p <partitions> [-f]')


def main():
    result_color = {'2': sty.fg.green,
                    '5': sty.bg.red + sty.fg.li_white
                    }
    output_path = './tmp/'
    source_path = '.'
    partitions = 4
    force_overwrite = False

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
                print(result_color.get(action_result.attrib['Index'], sty.fg.cyan) + result + sty.rs.all)

            try:
                os.makedirs(output_directory)
            except:
                pass
            file_exists = os.access(new_file, os.F_OK)
            if file_exists and force_overwrite == False:
                print(
                    sty.fg.yellow + new_file + ' already exists and --force flag not sent. File not being output.' + sty.rs.all)
            else:
                os.rename(file_with_path, new_file)

    print("\n\nFinished Processing Files.")


if __name__ == "__main__":
    main()
