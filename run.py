import argparse
import datetime
import inspect
import logging
import os
from typing import List
from types import SimpleNamespace

from tabulate import tabulate

import framework
from report import Report
from testcase import TestCase
from testcase_file import TestCaseFile


class Runner:
    def __init__(self) -> None:
        self.args: SimpleNamespace = None
        self.parser: argparse.ArgumentParser = None
        self.test_case_files: List[TestCaseFile] = []
        self.logger: logging.Logger = None
        self.framework_module_setup_tc: TestCase = None

    def parse_args(self):
        parser = argparse.ArgumentParser(
            add_help=False, usage=argparse.SUPPRESS,
            description="Runner Help"
        )
        parser.add_argument(
            '-d', '--logdir', help='Log directory (default $PWD/logs/<current-timestamp>)'
        )
        parser.add_argument(
            '-l', '--list', help='Print test case names', action='store_true'
        )
        parser.add_argument(
            '-h', '--help', help='Help Message', action='store_true'
        )
        parser.add_argument(
            'file_list', nargs='*',
            help='Test Case files, multiple files can be provided'
        )
        # framework must define a function "parse_args" that takes one
        # parameter (argumentParser)
        # and add all the arugments it expects into this parser using
        # (parser.add_argument)
        if getattr(framework, 'parse_args', None):
            framework.parse_args(parser)
        self.args, _ = parser.parse_known_args()
        self.parser = parser

    def parse_test_case_file_args(self, tc_file: TestCaseFile):
        # check if the test case file defines a function "parse_args".
        # If defined, call that function with an argumentParser object.
        # the function must add all the arguments it expects, into this parser
        tc_file_arg_parse_fn = getattr(tc_file.module, 'parse_args', None)
        if not tc_file_arg_parse_fn:
            return
        # create a new parser and let the test case add arguments to this parser
        tc_parser = argparse.ArgumentParser(
            add_help=False, usage=argparse.SUPPRESS,
            description=f"Parameters of Test Case {tc_file.file_name}"
        )
        # inside the test case file, the function "parse_args" must be defined
        # to take the parser argument and add arguments to it using
        # (parser.add_argument)
        tc_file_arg_parse_fn(tc_parser)
        tmp_args, _ = tc_parser.parse_known_args()
        tc_file.arg_parser = tc_parser
        tc_file.args = tmp_args

    def parse_test_case_files_args(self):
        for tc_file in self.test_case_files:
            self.parse_test_case_file_args(tc_file)

    def print_help(self):
        self.parser.print_help()
        print("")
        for tc_file in self.test_case_files:
            if tc_file.arg_parser:
                tc_file.arg_parser.print_help()
                print("")

    def list_py_files_in_dir(self, dir_name: str) -> List[str]:
        files_list: List[str] = []
        for fname in os.listdir(dir_name):
            if fname.endswith('.py'):
                files_list.append(os.path.join(dir_name, fname))
        return files_list

    def load_test_case_files(self):
        tmp_files_list: List[str] = []
        for fname in self.args.file_list:
            if os.path.isdir(fname):
                tmp_files_list.extend(self.list_py_files_in_dir(fname))
            else:
                tmp_files_list.append(fname)
        files_list = tmp_files_list
        for fname in sorted(files_list):
            fname = os.path.abspath(fname)
            tc_file = TestCaseFile(fname)
            self.test_case_files.append(tc_file)

    def print_testcases(self):
        data = []
        test_cases: List[TestCase] = []
        for tc_file in self.test_case_files:
            test_cases.extend(tc_file.get_test_cases())
        for idx, tc_obj in enumerate(test_cases, 1):
            data.append([
                idx, tc_obj.file_name, tc_obj.name, tc_obj.description
            ])
        print(tabulate(data, headers=[
              'Id', 'File', 'TestCase', 'Description']))

    def create_log_dir(self) -> str:
        start_time = datetime.datetime.now()
        cur_ts = start_time.strftime('%Y-%m-%d-%H-%M-%S')
        run_log_dir = os.path.join('logs', cur_ts)
        os.makedirs(run_log_dir, exist_ok=True)
        os.symlink(cur_ts, os.path.join('logs', 'latest'))
        return run_log_dir

    def run_test_case_files(self, log_dir: str = ""):
        if len(self.test_case_files) == 0:
            return
        if not log_dir:
            log_dir = self.create_log_dir()
        log_dir = os.path.abspath(log_dir)
        cwd = os.getcwd()
        for tc_file in self.test_case_files:
            os.chdir(cwd)
            self.logger.info("")
            self.logger.info(f"Planning to run {tc_file.file_name}")
            self.run_test_case_file(tc_file, log_dir)
            self.logger.info(f"Completed running {tc_file.file_name}")
            self.logger.info("")
        Report(self.test_case_files, log_dir)
        self.logger.info(f"Logs {log_dir}")

    def run_framework_module_setup(self, tc_file: TestCaseFile, log_dir: str):
        fn = getattr(framework, 'framework_module_setup', None)
        if not fn:
            return
        self.logger.info(
            f"--Running framework_module_setup for {tc_file.file_name}")
        fms_tc = TestCase(fn)
        self.framework_module_setup_tc = fms_tc
        # framework gets all the runner/framework args passed on the CLI
        fms_tc.args = self.args
        # framework needs to know what test case file/module its working for
        fms_tc.function_args = [tc_file.module]
        op = fms_tc.run(log_dir)
        # update tc_file with the output of the framework module setup
        tc_file.framework_module_setup_output = op
        self.logger.info(
            f"--Completed framework_module_setup for {tc_file.file_name}")

    def run_framework_module_cleanup(self, tc_file: TestCase, log_dir: str):
        fn = getattr(framework, 'framework_module_cleanup', None)
        if not fn:
            return
        fname = tc_file.file_name
        self.logger.info(f"--Running framework_module_cleanup for {fname}")
        TestCase(fn).run(log_dir)
        self.logger.info(f"--Completed framework_module_cleanup for {fname}")

    def run_test_case_file(self, tc_file: TestCaseFile, run_log_dir: str):
        # create a subdir for the tc file (module) under run_log_dir
        tc_file_log_dir = os.path.join(
            run_log_dir, inspect.getmodulename(tc_file.file_name))
        # run framework module setup before running the test case file
        self.run_framework_module_setup(tc_file, tc_file_log_dir)
        if self.framework_module_setup_tc and self.framework_module_setup_tc.status != "passed":
            self.logger.info(f"--Skipping test case file {tc_file.file_name}")
            return
        # if the framework has test_case_setup (and cleanup)
        # inform the tc_file to run these functions at the start/end
        # of each test case
        setup_fn = getattr(framework, 'framework_case_setup', None)
        if setup_fn:
            tc_file.framework_case_setup_tc = TestCase(setup_fn)
        cleanup_fn = getattr(framework, 'framework_case_cleanup', None)
        if cleanup_fn:
            tc_file.framework_case_cleanup_tc = TestCase(cleanup_fn)
        tc_count = len(tc_file.get_test_cases())
        self.logger.info(
            f"--Found {tc_count} test cases in {tc_file.file_name}")
        tc_file.run_test_cases(tc_file_log_dir)
        self.logger.info(
            f"--Completed {tc_count} test cases in {tc_file.file_name}")
        self.run_framework_module_cleanup(tc_file, tc_file_log_dir)

    def _create_logger(self):
        logger = logging.getLogger("runner")
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s %(message)s",
                                      datefmt="%Y-%m-%d-%H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        self.logger = logger

    def main(self):
        self.parse_args()
        self.load_test_case_files()
        self.parse_test_case_files_args()
        if self.args.list:
            self.print_testcases()
        elif self.args.help:
            self.print_help()
        else:
            self._create_logger()
            self.run_test_case_files()


if __name__ == "__main__":
    runner = Runner()
    runner.main()
