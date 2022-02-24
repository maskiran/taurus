import datetime
import inspect
import json
import logging
import os
import traceback
import types


class TestCase():
    def __init__(self, tc_function: types.FunctionType):
        self.file_name: str = inspect.getfile(tc_function)
        self.name: str = tc_function.__name__
        self.full_name: str = inspect.getmodulename(
            self.file_name) + '.' + self.name
        self.function: types.FunctionType = tc_function
        self.description: str = inspect.getdoc(tc_function)
        self.start_time: datetime.datetime = None
        self.end_time: datetime.datetime = None
        self.duration: int = ""
        self.status: str = ""
        self.error: str = ""
        self.logger: logging.Logger = ""
        self.log_dir: str = ""
        self.log_file: str = ""
        self.framework_module_setup_output = ""
        self.test_module_setup_output = ""
        self.framework_case_setup_output = ""
        self.test_case_setup_output = ""
        self.output = None
        self.args = None

    def run(self, log_dir: str, log_file: str = None):
        self.start_time = datetime.datetime.now()
        self.logger = self._create_logger(log_dir, log_file)
        self.logger.info(f'Start {self.full_name}')
        tc_output = None
        try:
            tc_output = self.function(self)
            self.status = "passed"
        except Exception as err:
            self.status = "failed"
            self.error = traceback.format_exc()
            self.logger.exception(err)
        self.end_time = datetime.datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.logger.info('End %s, Status %s',
                         self.full_name, self.status)
        self.output = tc_output
        return tc_output

    def _create_logger(self, log_dir: str, log_file: str,
                       stdout: bool = True) -> logging.Logger:
        """
        Create a FileHandler logger object. If stdout is True, add
        an additional streamhandler in the logger.
        """
        self.log_dir = log_dir
        if not log_file:
            log_file = self.name
        self.log_file = os.path.join(log_dir, log_file)
        os.makedirs(self.log_dir, exist_ok=True)
        logger = logging.Logger(self.log_file)
        handler = logging.FileHandler(self.log_file)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s",
                                      datefmt="%Y-%m-%d-%H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        if stdout:
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def __repr__(self) -> str:
        return json.dumps(self.to_json(), indent=4)

    def to_json(self):
        """
        JSON Encoder
        """
        return {
            'file_name': self.file_name,
            'name': self.name,
            'full_name': self.full_name,
            'args': self.args.__dict__,
            'description': self.description,
            'start_time': str(self.start_time),
            'end_time': str(self.end_time),
            'duration': self.duration,
            'status': self.status,
            'error': self.error,
            'log_file': self.log_file,
            'log_dir': self.log_dir
        }
