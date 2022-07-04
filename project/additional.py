import csv
import datetime
import os
import shutil
import tempfile
import zipfile
from typing import Union

import pkg_resources

from fastapi import Request


class ApiLogger:

    logs_path = pkg_resources.resource_filename("project", "") + f"/{os.environ.get('LOGS_DIR_NAME')}"

    @classmethod
    def create_main_logs_dir(cls):
        if not os.path.exists(cls.logs_path):
            print("Creating logs directory")
            os.mkdir(cls.logs_path)

    @classmethod
    def create_module_log(cls, module: Union[Request, str], msg: str,
                          log_type: str = 'work'):
        cls.create_main_logs_dir()
        if not 3 <= len(log_type) <= 20:
            raise ValueError("Module name must be between 3 to 20 characters in length")
        if not isinstance(module, (str, Request)):
            raise TypeError("Argument 'module' has to be str or Request")
        if not isinstance(msg, str):
            raise TypeError("Argument 'msg' has to be of type str")
        log_dir_path = cls.logs_path + f"/{datetime.date.today().isoformat()}"
        if not os.path.exists(log_dir_path):
            os.mkdir(log_dir_path)

        if type(module) == Request:
            with open(file=f"{log_dir_path}/{module.url.path.split('/')[1]}.{log_type}.log", mode="a+", encoding="utf-8") as logfile:
                msg = f"\n[{datetime.datetime.now().isoformat(sep='#', timespec='seconds')}]" \
                      f" {module.url.path}: {msg} \n" \
                      f"Request url: {module.url}\n" \
                      f"Request path params: {module.path_params}\n" \
                      f"Request query params: {module.query_params}\n" \
                      f"Request headers: {module.headers}\n"
                logfile.write(msg)

        elif type(module) == str:
            with open(file=f"{log_dir_path}/{module}.{log_type}.log", mode="a+", encoding="utf-8") as logfile:
                msg = f"\n[{datetime.datetime.now().isoformat(sep='#', timespec='seconds')}]" \
                      f" {module}: {msg} \n"
                logfile.write(msg)


def create_temp_csv(data: list, filename: str, column_names: list[str]) -> None:
    if not isinstance(data, list):
        raise TypeError(f"Input must be dict, got {type(data)}")
    if not isinstance(column_names, list):
        raise TypeError(f"Column names have to be list of str, got {type(column_names)}")
    current_path = os.path.dirname(os.path.realpath(__file__))
    tmp_dir = tempfile.mkdtemp(dir=current_path)
    compressed_file = f"{filename}.zip"
    os.chdir(tmp_dir)
    zip_file = zipfile.ZipFile(compressed_file, 'w')
    csv_filename = f"{filename}.csv"

    with open(f"{tmp_dir}/{csv_filename}", 'w', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=column_names)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    zip_file.write(f'{tmp_dir}/{csv_filename}', compress_type=zipfile.ZIP_DEFLATED,
                   arcname=os.path.basename(f"{tmp_dir}/{csv_filename}.csv"))
    zip_file.close()
    return compressed_file, tmp_dir


def delete_temp_files(temp_files_dir: str):
    shutil.rmtree(temp_files_dir)
