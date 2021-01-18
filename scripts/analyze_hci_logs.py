import os
import json

# buncha opcodes
opcodes = {
'0x00000001':'BT_ATT_OP_ERROR_RSP',
'0x00000002':'BT_ATT_OP_MTU_REQ',
'0x00000003':'BT_ATT_OP_MTU_RSP',
'0x00000004':'BT_ATT_OP_FIND_INFO_REQ',
'0x00000005':'BT_ATT_OP_FIND_INFO_RSP',
'0x00000006':'BT_ATT_OP_FIND_BY_TYPE_VAL_REQ',
'0x00000007':'BT_ATT_OP_FIND_BY_TYPE_VAL_RSP',
'0x00000008':'BT_ATT_OP_READ_BY_TYPE_REQ',
'0x00000009':'BT_ATT_OP_READ_BY_TYPE_RSP',
'0x0000000a':'BT_ATT_OP_READ_REQ',
'0x0000000b':'BT_ATT_OP_READ_RSP',
'0x0000000c':'BT_ATT_OP_READ_BLOB_REQ',
'0x0000000d':'BT_ATT_OP_READ_BLOB_RSP',
'0x0000000e':'BT_ATT_OP_READ_MULT_REQ',
'0x0000000f':'BT_ATT_OP_READ_MULT_RSP',
'0x00000010':'BT_ATT_OP_READ_BY_GRP_TYPE_REQ',
'0x00000011':'BT_ATT_OP_READ_BY_GRP_TYPE_RSP',
'0x00000012':'BT_ATT_OP_WRITE_REQ',
'0x00000013':'BT_ATT_OP_WRITE_RSP',
'0x00000052':'BT_ATT_OP_WRITE_CMD',
'0x000000d2':'BT_ATT_OP_SIGNED_WRITE_CMD',
'0x00000016':'BT_ATT_OP_PREP_WRITE_REQ',
'0x00000017':'BT_ATT_OP_PREP_WRITE_RSP',
'0x00000018':'BT_ATT_OP_EXEC_WRITE_REQ',
'0x00000019':'BT_ATT_OP_EXEC_WRITE_RSP',
'0x0000001b':'BT_ATT_OP_HANDLE_VAL_NOT',
'0x0000001d':'BT_ATT_OP_HANDLE_VAL_IND',
'0x0000001e':'BT_ATT_OP_HANDLE_VAL_CONF',
}

project_root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
logs_dir = project_root_dir + "/logs"

# BUNCHA SHIT FOR COMPARING LOGS
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
    log_str = 'log {}: source:{}\tdest:{}\topcode:{}'.format(ind, obj['source'], obj['dest'], opcodes[obj['opcode']])
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


# JUST WANT TO SEE COMMANDS SENT TO THE SLIDER THAT HAVE A VALUE
# ALSO FORMAT THE COMMANDS FOR PYTHON
for index in range(0, len(log_contents[0])):
    datum = log_contents[0][index]
    if 'value' in datum.keys() and datum['dest'] == 'SldrOne':
        value = "bytes(b'\\x{}')".format(datum['value'].replace(':', '\\x'))
        print("await client.write_gatt_char(IO_CTRL_CHARACTERISTIC_UUID, {}) #{}".format(value, opcodes[datum['opcode']]))
    elif datum['dest'] == 'SldrOne':
        print("await client.write_gatt_char(IO_CTRL_CHARACTERISTIC_UUID, bytearray()), #{}".format(opcodes[datum['opcode']]))


