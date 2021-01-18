import os
import json

project_root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
logs_dir = project_root_dir + "/logs"

hci_files = []
for path, subdirs, files in os.walk(logs_dir):
    for name in files:
        if "_hci_" in name:
            hci_files.append(os.path.join(path, name))
hci_files.sort()

log_contents = []
for file_handle in hci_files:
    with open(file_handle, 'r') as f:
        log_contents.append(json.load(f))

max_length = 0
for log_json in log_contents:
    max_length = max(max_length, len(log_json))

def get_log_line(ind, obj):
    log_str = 'log {}: source:{}\tdest:{}\topcode:{}'.format(ind, obj['source'], obj['dest'], obj['opcode'])
    if 'value' in obj.keys():
        log_str += '\tvalue:{}'.format(obj['value'])
    return log_str

out_lines = []
for index in range(0, max_length):
    out_lines.append('Event {}\r'.format(index))
    for log_file_index in range(0, len(log_contents)):
        log_json = log_contents[log_file_index]
        if index < len(log_json):
            out_lines.append(get_log_line(log_file_index + 1, log_json[index]) + '\r')
    out_lines.append('\r')

with open(logs_dir + '/analysis/hci_comparison.txt', 'w') as analysis_file:
    analysis_file.writelines(out_lines)