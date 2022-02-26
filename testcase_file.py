import argparse
import datetime
import inspect
import importlib.util
import logging
import os
from typing import List
from types import ModuleType

from testcase import TestCase


def import_file(file_path: str):
    """
    Import the python file and return the module object
    :param file_path: full path of the python file to import
    :return: module object
    """
    module_name = inspect.getmodulename(file_path)
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestCaseFile(object):
    def __init__(self, file_name: str) -> None:
        self._special_test_cases = ["test_module_setup", "test_module_cleanup",
                                    "test_case_setup", "test_case_cleanup"]
        self.file_name: str = file_name
        self.module: ModuleType = import_file(file_name)
        self.test_case_list: List[TestCase] = self._load_test_cases()
        # filled by run.py when it loads the framework
        self.framework_module_setup_output = None
        self.framework_case_setup_tc: TestCase = None
        self.framework_case_cleanup_tc: TestCase = None
        # store this for convenience as its accessed by test case
        self.test_module_setup_tc: TestCase = None
        # cli argument parser (added by run.py during the run)
        self.arg_parser = None
        self.args: argparse.Namespace = argparse.Namespace()
        self.log_dir = ""
        self.start_time: datetime.datetime = None
        self.end_time: datetime.datetime = None
        self.duration: int = 0
        self.logger = logging.getLogger("runner")

    def _load_test_cases(self) -> List[TestCase]:
        func_list = inspect.getmembers(self.module, inspect.isfunction)
        test_case_list: List[TestCase] = []
        for func_name, func_obj in func_list:
            # get all the functions that start with test_
            if not func_name.startswith('test_'):
                continue
            testcase_obj = TestCase(func_obj)
            test_case_list.append(testcase_obj)
        return test_case_list

    def _find_test_case(self, test_case_name: str) -> TestCase:
        matched_tc = None
        for tc in self.test_case_list:
            if tc.name == test_case_name:
                matched_tc = tc
                break
        return matched_tc

    def get_test_cases(self, special=False) -> List[TestCase]:
        if special == True:
            return self.test_case_list
        test_cases = []
        for tc in self.test_case_list:
            if tc.name in self._special_test_cases:
                continue
            test_cases.append(tc)
        return test_cases

    def run_test_module_setup(self):
        self.test_module_setup_tc = self._find_test_case("test_module_setup")
        if not self.test_module_setup_tc:
            return
        self.logger.info(
            f"--Running test_module_setup from {self.file_name}")
        # pass the output of the framework module setup into this
        self.test_module_setup_tc.framework_module_setup_output = self.framework_module_setup_output
        self.test_module_setup_tc.run(self.log_dir)
        self.logger.info(
            f"--Completed test_module_setup from {self.file_name}")

    def run_test_case(self, tc: TestCase):
        # let the test case know about the other init/cleanup tests that it need to run
        tc.framework_case_setup_tc = self.framework_case_setup_tc
        tc.framework_case_cleanup_tc = self.framework_case_cleanup_tc
        tc.test_case_setup_tc = self._find_test_case("test_case_setup")
        tc.test_case_cleanup_tc = self._find_test_case("test_case_cleanup")
        # pass the outputs from the module setups to the test case
        tc.framework_module_setup_output = self.framework_module_setup_output
        if self.test_module_setup_tc:
            tc.test_module_setup_output = self.test_module_setup_tc.output
        tc.args = self.args
        self.logger.info(
            f"--Running test_case {tc.name} from {self.file_name}")
        tc.run(self.log_dir)
        self.logger.info(
            f"--Completed test_case {tc.name} from {self.file_name}")

    def run_test_module_cleanup(self):
        test_module_cleanup_tc = self._find_test_case("test_module_cleanup")
        if not test_module_cleanup_tc:
            return
        self.logger.info(
            f"--Running test_module_cleanup from {self.file_name}")
        test_module_cleanup_tc.run(self.log_dir)
        self.logger.info(
            f"--Completed test_module_cleanup from {self.file_name}")

    def run_test_cases(self, log_dir) -> None:
        self.log_dir = log_dir
        os.chdir(os.path.dirname(self.file_name))
        self.start_time = datetime.datetime.now()
        self.run_test_module_setup()
        if self.test_module_setup_tc and self.test_module_setup_tc.status != "passed":
            # dont run other test cases if the module's setup failed
            self.logger.info(f"--Skipping test case file {self.file_name}")
            return
        for tc in self.get_test_cases():
            self.run_test_case(tc)
        self.run_test_module_cleanup()
        self.end_time = datetime.datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()

    def to_json(self):
        # test case has its own json encoder
        return {
            'file_name': self.file_name,
            'args': self.args.__dict__ or {},
            'log_dir': self.log_dir,
            'start_time': str(self.start_time),
            'end_time': str(self.end_time),
            'duration': self.duration,
            'test_cases': self.get_test_cases()
        }
