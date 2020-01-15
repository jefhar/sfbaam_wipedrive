import os
import xml.etree.ElementTree as ET


def file_to_path(_file_name):
    _directory = '/'
    for x in range(0, 4):
        _directory = _directory + _file_name[x] + '/'
    return _directory


regular_text = '\033[1;m'
success_text = '\033[1;32m'
error_text = '\033[1;41m'
info_text = '\033[1;33m'

result_color = {'2': success_text,
                '5': error_text
                }

path = '.' # todo: make this default to command line argument #1
dirs = os.listdir(os.getcwd())
for file in dirs:
    if file.endswith('xml'):
        print('Processing ' + file)
        tree = ET.parse(file)
        Reports = tree.getroot()
        Job = Reports.find('Report').find('Jobs').find('Job')
        size = Job.find('Operation').find('Gigabytes').text
        directory = file_to_path(file)
        directory = './tmp/' + size + directory
        new_file = directory + file
        # print('Create `' + directory + '`')
        # print('Move `' + file + '` to `' +newfile +'`')
        print("\n+" + new_file, end='')
        print(' - ' + size + 'GB drives.')
        for Operation in Job.findall('Operation'):
            Gigabytes = Operation.find('Gigabytes')
            Serial = Operation.find('Serial')
            ActionResult = Operation.find('ActionResult')
            result = "Success" if (ActionResult.attrib['Index'] == '2') else "Failure"

            print("|--> " + Serial.text + ' - ' + Gigabytes.text + "GB; Result: ", end='')
            print (result_color.get(ActionResult.attrib['Index'], info_text) + result + regular_text)

        try:
            os.makedirs(directory)
        except:
            pass
        os.rename(file, new_file)

print("\n\nFinished Processing Files.")
