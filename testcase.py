import argparse
import datetime
import inspect
import json
import logging
import os
import traceback
from types import FunctionType
from typing import List


class TestCase():
    def __init__(self, tc_function: FunctionType):
        self.file_name: str = inspect.getfile(tc_function)
        self.name: str = tc_function.__name__
        self.full_name: str = inspect.getmodulename(
            self.file_name) + '.' + self.name
        self.function: FunctionType = tc_function
        # function is expected to have 1 arg (self).
        # function_args is the extra arguments that will be passed to the
        # function. usually used by framework functions
        self.function_args = []
        self.description: str = inspect.getdoc(tc_function)
        self.start_time: datetime.datetime = None
        self.end_time: datetime.datetime = None
        self.duration: int = ""
        self.status: str = ""
        self.error: str = ""
        self.logger: logging.Logger = ""
        self.log_dir: str = ""
        self.log_file: str = ""
        # the cli args (argparse.Namespace)
        self.args: argparse.Namespace = argparse.Namespace()
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
        # store the state of each individual setup/cleanup and run the next one
        # only if the previous state succeeded
        self._state = {
            "framework_case_setup": "passed",
            "test_case_setup": "passed",
            "framework_case_cleanup": "passed",
            "test_case_cleanup": "passed",
        }

    def _run_tc(self, tc: 'TestCase', role: str = "", pre: str = "",
                post: str = "", function_args: List = None):
        # tc - TestCase to run
        # role - a help str thats printed defining the role of the tc
        # pre - state key whose value must evaluate to "passed" before the test can run
        # post - state key whose value is set at the end of the test run
        # function_args - list of args passed to the test function (expanded as *args)
        if not tc:
            return
        if function_args is None:
            function_args = []
        rlog = logging.getLogger("runner")
        info_str = f"{role} {tc.full_name}"
        if tc.full_name != self.full_name:
            # a different helper test (set up and cleanup) is being run
            info_str = f"{role} helper {tc.full_name} for {self.full_name}"
        rlog.info(f"----Running {info_str}")
        self.logger.info(f'Running {info_str}')
        output = None
        try:
            # no pre condition or precondition has passed
            if pre is None or self._state[pre] == "passed":
                output = tc.function(self, *function_args)
                if post:
                    self._state[post] = "passed"
            else:
                rlog.info(
                    f"----Skipping {info_str} as pre-condition {pre} failed/skipped")
                self.logger.info(
                    f"Skipping {info_str} as pre-condition {pre} failed/skipped")
                self.status = "failed"
                self._state[post] = "skipped"
        except Exception as err:
            self.status = "failed"
            if post:
                self._state[post] = "failed"
            self.error = traceback.format_exc()
            rlog.exception(err)
            self.logger.exception(err)

        self.logger.info(f'Completed {info_str}')
        rlog.info(f"----Completed {info_str}")
        return output

    def run(self, log_dir: str):
        self.start_time = datetime.datetime.now()
        self.logger = self._create_logger(log_dir)
        self.logger.info(f'Start Test Case {self.full_name}')
        # run the init/setup functions
        self.framework_case_setup_output = self._run_tc(
            self.framework_case_setup_tc, role='framework_case_setup',
            pre=None, post='framework_case_setup')
        self.test_case_setup_output = self._run_tc(
            self.test_case_setup_tc, role='test_case_setup',
            pre='framework_case_setup', post='test_case_setup')
        # run the current function
        self.output = self._run_tc(
            self, role='function',
            pre='test_case_setup', post=None, function_args=self.function_args)
        # run the cleanup functions
        self._run_tc(self.test_case_cleanup_tc, role='test_case_cleanup',
                     pre='test_case_cleanup', post=None)
        self._run_tc(self.framework_case_cleanup_tc, role='framework_case_cleanup',
                     pre='framework_case_cleanup', post=None)
        # if there is no error so far, the status would have been empty,
        # mark it as passed
        if self.status == "":
            self.status = "passed"
        self.end_time = datetime.datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.logger.info('End test Case %s, Status %s',
                         self.full_name, self.status)
        return self.output

    def _create_logger(self, log_dir: str) -> logging.Logger:
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
