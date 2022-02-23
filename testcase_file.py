import datetime
import inspect
import importlib.util
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
        self.test_module_setup: TestCase = self._find_test_case(
            "test_module_setup")
        self.test_module_cleanup: TestCase = self._find_test_case(
            "test_module_cleanup")
        self.test_case_setup: TestCase = self._find_test_case(
            "test_case_setup")
        self.test_case_cleanup: TestCase = self._find_test_case(
            "test_case_cleanup")
        self.arg_parser = None
        self.args = None
        self.start_time: datetime.datetime = None
        self.end_time: datetime.datetime = None
        self.duration: int = 0
        self.log_dir = ""

    def _load_test_cases(self) -> List[TestCase]:
        func_list = sorted(dir(self.module))
        test_case_list: List[TestCase] = []
        for func_name in func_list:
            # get all the functions that start with test_
            if not func_name.startswith('test_'):
                continue
            func_obj = getattr(self.module, func_name)
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

    def run(self, log_dir: str) -> None:
        os.chdir(os.path.dirname(self.file_name))
        self.log_dir = os.path.join(log_dir, inspect.getmodulename(self.file_name))
        self.start_time = datetime.datetime.now()
        print(f"\n====Running {self.file_name}====")
        mod_setup_out = None
        if self.test_module_setup:
            print(f"\n----Running {self.file_name} test_module_setup----")
            mod_setup_out = self.test_module_setup.run(self.log_dir)
        for tc in self.get_test_cases():
            tc.args = self.args
            tc.module_setup_output = mod_setup_out
            print(f"\n----Running {self.file_name} {tc.name}----")
            tc.run(self.log_dir, self.test_case_setup, self.test_case_cleanup)
        if self.test_module_cleanup:
            print(f"\n----Running {self.file_name} test_module_cleanup----")
            self.test_module_cleanup.run(self.log_dir)
        print(f"\n====Completed {self.file_name}====")
        self.end_time = datetime.datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()

    def to_json(self):
        # test case has its own json encoder
        return {
            'file_name': self.file_name,
            'args': self.args.__dict__,
            'log_dir': self.log_dir,
            'start_time': str(self.start_time),
            'end_time': str(self.end_time),
            'duration': self.duration,
            'test_cases': self.get_test_cases()
        }
