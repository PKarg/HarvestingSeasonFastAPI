import datetime
import os
import pkg_resources
import pathlib


class ApiLogger:

    logs_path = pkg_resources.resource_filename("project", "") + f"/{os.environ.get('LOGS_DIR_NAME')}"

    @classmethod
    def create_main_logs_dir(cls):
        if not os.path.exists(cls.logs_path):
            print("Creating logs directory")
            os.mkdir(cls.logs_path)

    @classmethod
    def create_module_exception_log(cls, module: str, exc: str):
        log_dir_path = cls.logs_path + f"/{datetime.date.today().isoformat()}"
        if not os.path.exists(log_dir_path):
            os.mkdir(log_dir_path)
        with open(file=f"{log_dir_path}/{module}.log", mode="a+", encoding="utf-8") as logfile:
            msg = f"[{datetime.datetime.now().isoformat(sep='#', timespec='seconds')}] Excepion occured: {exc} \n"
            logfile.write(msg)
