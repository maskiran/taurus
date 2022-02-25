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
        self.args = None
        # different init/cleanup test cases that can be run
        self.framework_case_setup_tc: TestCase = None
        self.test_case_setup_tc: TestCase = None
        self.framework_case_cleanup_tc: TestCase = None
        self.test_case_cleanup_tc: TestCase = None
        # outputs from different init functions that are run before the test case
        self.framework_module_setup_output = ""
        self.test_module_setup_output = ""
        self.framework_case_setup_output = ""
        self.test_case_setup_output = ""
        # this test case's run output
        self.output = None

    def _run_and_log_tc_function(self, tc: 'TestCase', help_str: str):
        if not tc:
            return
        rlog = logging.getLogger("runner")
        rlog.info(f"----Running {help_str} for {self.name}")
        self.logger.info(f'Running {help_str} {tc.full_name}')
        output = tc.function(self)
        self.logger.info(f'Completed {help_str} {tc.full_name}')
        rlog.info(f"----Completed {help_str} for {self.name}")
        return output

    def run(self, log_dir: str):
        self.start_time = datetime.datetime.now()
        self.logger = self._create_logger(log_dir)
        self.logger.info(f'Start Test Case {self.full_name}')
        try:
            # run the init/setup functions
            self.framework_case_setup_output = self._run_and_log_tc_function(
                self.framework_case_setup_tc, 'framework_case_setup')
            self.test_case_setup_output = self._run_and_log_tc_function(
                self.test_case_setup_tc, 'test_case_setup')
            # run the current function
            self.output = self._run_and_log_tc_function(
                self, 'test_case_function')
            self.status = "passed"
        except Exception as err:
            self.status = "failed"
            self.error = traceback.format_exc()
            self.logger.exception(err)
        finally:
            # run the cleanup functions
            self._run_and_log_tc_function(
                self.test_case_cleanup_tc, 'test_case_cleanup')
            self._run_and_log_tc_function(
                self.framework_case_cleanup_tc, 'framework_case_cleanup')
        self.end_time = datetime.datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.logger.info('End test Case %s, Status %s',
                         self.full_name, self.status)
        return self.output

    def _create_logger(self, log_dir: str, stdout: bool = False) -> logging.Logger:
        """
        Create a FileHandler logger object. If stdout is True, add
        an additional streamhandler in the logger.
        """
        self.log_dir = log_dir
        self.log_file = os.path.join(log_dir, self.name)
        os.makedirs(self.log_dir, exist_ok=True)
        logger = logging.getLogger(self.log_file)
        logger.setLevel(logging.DEBUG)
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
            'args': self.args.__dict__ or {},
            'description': self.description,
            'start_time': str(self.start_time),
            'end_time': str(self.end_time),
            'duration': self.duration,
            'status': self.status,
            'error': self.error,
            'log_file': self.log_file,
            'log_dir': self.log_dir
        }
