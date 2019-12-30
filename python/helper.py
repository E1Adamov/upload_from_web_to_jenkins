import os
import shutil
from datetime import datetime as dt

import config


def get_temp_dir_path(dir_name: str) -> str:
    server_dir = get_server_location()
    return os.path.join(server_dir, config.TEMP, dir_name)


def clear_dir(path: str):
    for folder, sub_folders, file_names in os.walk(path):
        for sub_folder in sub_folders:
            sub_folder_path = os.path.join(path, sub_folder)
            shutil.rmtree(sub_folder_path, ignore_errors=True)
            print(f'Deleted directory {sub_folder_path}')

        for file_name in file_names:
            file_path = os.path.join(path, file_name)
            os.remove(file_path)
            print(f'Deleted file {file_path}')


def get_file_timestamp() -> str:
    return dt.now().strftime('%Y%m%d%H%M%S%f')


def get_raw_timestamp() -> dt:
    return dt.now()


def save_bin_to_file(bin_data: bytes, file_path: str):
    with open(file_path, 'wb') as f:
        f.write(bin_data)


def empty_dir(path: str):
    for file_name in os.listdir(path):
        file_path = os.path.join(path, file_name)
        if os.path.isfile(file_path):
            os.unlink(file_path)


def get_server_location() -> str:
    split_path = os.path.normpath(__file__).split(os.sep)
    return os.sep.join(split_path[:split_path.index('python')])


def log(text: str):
    if not text:
        return

    for line in text.splitlines():
        print(line)


def parse_multipart(request) -> dict:
    reader = await request.multipart()

    fields = {'alt_d_file': dict(), 'support_files': []}

    while True:
        part = await reader.next()

        if part is None:
            break

        part_type = 'file' if part.filename else 'text'

        if part_type == 'text':
            fields[part.name] = await part.text()

        elif part_type == 'file':
            if part.name == 'altDDumpFile':
                fields['alt_d_file']['name'] = part.filename
                fields['alt_d_file']['data'] = await part.read()
            else:
                support_file_dict = {'name': part.filename, 'data': await part.read()}
                fields['support_files'].append(support_file_dict)

    return fields
