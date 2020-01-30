#!/usr/bin/env python3
import datetime
import getopt
import logging
import os
import shutil
import sys
import time
import xml.etree.ElementTree as ET


def file_to_path(_file_name, _partitions):
    _directory = '/'
    for x in range(0, _partitions):
        _directory = _directory + _file_name[x] + '/'
    return _directory


def seconds_per_gig(time_string, size):
    time_portions = time_string.split(':')
    time_seconds = int(time_portions[0]) * 3600 + int(time_portions[1]) * 60 + int(time_portions[2])
    s_p_g = time_seconds / float(size)
    return s_p_g


def record_serials(output_path, serials, size, result):
    output_directory = output_path + 'reports/'
    try:
        os.makedirs(output_directory)
    except:
        pass
    f = open(output_directory + size + '.txt', 'a+t')
    for i in range(len(serials)):
        print("{serial}:{result}".format(serial=serials[i], result=result), file=f)


def usage():
    print('usage: move_wipedrive_xml.py -s <sourcePath> -o <outputPath> -p <partitions> [-f]')


def main():
    logging.basicConfig(filename='move_wipedrive.log', level=logging.DEBUG)
    output_path = './tmp/'
    source_path = '.'
    partitions = 4
    force_overwrite = False
    success = 0
    failure = 0
    unknown = 0
    unverified = 0

    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hfs:o:p:",
            ['help', 'force', 'sourcepath=', 'outputpath=', 'partitions=']
        )
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

    logging.info("Beginning moving process.")
    logging.info("source_path: " + source_path)
    logging.info("output_path: " + output_path)
    logging.info("partitions: " + str(partitions))
    logging.info("force: " + str(force_overwrite))

    start = time.time()
    for file in os.listdir(source_path):
        file_with_path = source_path + '/' + file
        if file_with_path.endswith('xml'):
            xml = file_with_path
            original_file_parts = xml.split('.')
            pdf = original_file_parts[0] + '.pdf'  # Need to know if -s contains a '.', though.
            logging.debug(xml)
            logging.debug(pdf)
            file_output_path = output_path
            drive_serials = []

            print('Processing ' + xml)
            logging.info("Processing " + xml)
            try:
                tree = ET.parse(xml)
            except ET.ParseError as e:
                logging.error(e)
                logging.warning('Skipping ' + xml + ' as not well-formed.')
                continue
            job = tree.getroot().find('Report').find('Jobs').find('Job')
            size = job.find('Operation').find('Gigabytes').text
            server_serial = tree.getroot().find('Report').find('Hardware').find('ComputerSerial').text
            server_serial = server_serial.replace('/', '_')
            start_time = tree.getroot().find('Report').find('Jobs').find('Job').find('Operation').find('StartTime').text
            # <StartTime>Saturday, 04 Jan 2020 14:28:24</StartTime>
            time_obj = datetime.datetime.strptime(start_time, '%A, %d %b %Y %H:%M:%S')
            job_datetime = time_obj.strftime('%Y%m%d%H%M%S')
            had_error = False
            gigabytes = 0

            for Operation in job.findall('Operation'):
                gigabytes = Operation.find('Gigabytes').text
                drive_serial = Operation.find('Serial').text
                drive_serials = drive_serials + [drive_serial]
                action_result = int(Operation.find('ActionResult').attrib['Index'])
                method_type = Operation.find('NISTMethodType').text
                type_reason = Operation.find('NISTMethodTypeReason').text
                if type_reason is None:
                    type_reason = 'Unknown'

                if action_result == 2:
                    result = "Success"
                    success = success + 1
                    logging.debug(xml + " : " + drive_serial + " : " + result)
                elif action_result == 5:
                    result = "Failure"
                    failure = failure + 1
                    logging.debug(xml + " : " + drive_serial + " : " + result)
                    if type_reason == "Wipe did not complete successfully.":
                        method_type = "Failure"
                else:
                    result = "Unknown"
                    unknown = unknown + 1
                    logging.debug(xml + " : " + drive_serial + " : " + result)

                if method_type == 'Unknown':
                    if not had_error:
                        file_output_path = file_output_path + '/' + type_reason.replace(' ', '').replace('.', '')
                        had_error = True
                    result = result + ': ' + type_reason
                    unverified = unverified + 1

                result = result
                output_directory = file_output_path + '/' + size + file_to_path(server_serial, partitions)
                logging.debug("|--> " + drive_serial + ' - ' + gigabytes + "GB; Result:  " + result)
            try:
                os.makedirs(output_directory)
            except:
                pass

            new_file_name = output_directory + '/' + server_serial + '_' + job_datetime
            output_xml = new_file_name + '.xml'
            output_pdf = new_file_name + '.pdf'

            logging.debug(file + " to " + output_xml)
            logging.debug(xml + ' has ' + size + 'GB drives.')

            # if os.access(output_xml, os.F_OK) and force_overwrite is False:
            #     logging.warning(
            #         output_xml + ' already exists and --force flag not sent. File not being output.')
            # else:
            #     os.rename(xml, output_xml)
            #     logging.info('Copying `' + xml + '` to `' + output_xml + '`')

            if os.access(output_pdf, os.F_OK) and force_overwrite is False:
                logging.warning(
                    output_pdf + ' already exists and --force flag not sent. File not being output.')
            else:
                record_serials(output_path, drive_serials, gigabytes, result)
                try:
                    os.rename(pdf, output_pdf)
                    logging.debug('Copying `' + pdf + '` to `' + output_pdf + '`')
                except:
                    logging.warning(pdf + ' Does Not Exist. Please recreate it from `' + xml + '`.')
                    try:
                        os.makedirs(file_output_path + "/missing/")
                    except:
                        pass
                    shutil.copy(xml, file_output_path + "/missing/")

    print("\n\nFinished Processing Files.")
    end = time.time()
    total = success + failure + unknown
    logging.info("Complete.")
    print("Successful: {success} ({:02.3f}%)".format(success * 100 / total, success=success))
    logging.info("Successful: {success} ({:02.3f}%)".format(success * 100 / total, success=success))
    print("Failed: {failure} ({:02.3f}%)".format(failure * 100 / total, failure=failure))
    logging.info("Failed: {failure} ({:02.3f}%)".format(failure * 100 / total, failure=failure))
    if unknown > 0:
        print("Unknown: {unknown} ({:02.3f}%)".format(failure * 100 / total, unknown=unknown))
        logging.info("Unknown: {unknown} ({:02.3f}%)".format(failure * 100 / total, unknown=unknown))
    if unverified > 0:
        print("Total unverified: {unverified} ({:02.3f}%)".format(unverified * 100 / total, unverified=unverified))
        logging.info(
            "Total unverified: {unverified} ({:02.3f}%)".format(unverified * 100 / total, unverified=unverified))
    print("Total drives: {total}".format(total=total))
    logging.info("Total drives: {total}".format(total=total))
    logging.info("Complete in {s} seconds.".format(s=end - start))


if __name__ == "__main__":
    main()
