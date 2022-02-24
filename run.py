import argparse
import datetime
import inspect
import os
from typing import List

from tabulate import tabulate

import framework
from report import Report
from testcase import TestCase
from testcase_file import TestCaseFile


def parse_args():
    """
    Parse the command line arguments and return the arguments in namespace
    """
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
    args, tc_args = parser.parse_known_args()
    return (parser, args, tc_args)


def parse_test_case_args(test_case_files: List[TestCaseFile], tc_args: List):
    for tc_file in test_case_files:
        # check if the test case file defines a function "parse_args".
        # If defined, call that function with an argumentParser object.
        # the function adds all the arguments it expects, into this parser
        tc_file_arg_parse_fn = getattr(tc_file.module, 'parse_args', None)
        if not tc_file_arg_parse_fn:
            continue
        # create a new parser and let the test case add arguments to this parser
        tc_parser = argparse.ArgumentParser(
            add_help=False, usage=argparse.SUPPRESS,
            description=f"Parameters of Test Case {tc_file.file_name}"
        )
        # inside the test case file, the function "parse_args" must be defined
        # to take the parser argument and add arguments to itusing
        # (parser.add_argument)
        tc_file_arg_parse_fn(tc_parser)
        tmp_args, _ = tc_parser.parse_known_args(tc_args)
        tc_file.arg_parser = tc_parser
        tc_file.args = tmp_args


def print_help(parser: argparse.ArgumentParser,
               test_case_files: List[TestCaseFile]):
    parser.print_help()
    print("")
    for tc_file in test_case_files:
        if tc_file.arg_parser:
            tc_file.arg_parser.print_help()
            print("")


def list_py_files_in_dir(dir_name: str) -> List[str]:
    files_list: List[str] = []
    for fname in os.listdir(dir_name):
        if fname.endswith('.py'):
            files_list.append(os.path.join(dir_name, fname))
    return files_list


def load_test_case_files(files_list: List[str]) -> List[TestCaseFile]:
    tmp_files_list: List[str] = []
    for fname in files_list:
        if os.path.isdir(fname):
            tmp_files_list.extend(list_py_files_in_dir(fname))
        else:
            tmp_files_list.append(fname)
    files_list = tmp_files_list
    test_case_files: List[TestCaseFile] = []
    for fname in sorted(files_list):
        cmps = os.path.split(fname)
        if cmps[-1] == 'init.py':
            # ignore any file that's named as init.py
            continue
        fname = os.path.abspath(fname)
        loaded_tc_file = TestCaseFile(fname)
        test_case_files.append(loaded_tc_file)

    return test_case_files


def print_testcases(test_case_files: List[TestCaseFile]):
    data = []
    test_cases: List[TestCase] = []
    for tc_file in test_case_files:
        test_cases.extend(tc_file.get_test_cases())
    for idx, tc_obj in enumerate(test_cases, 1):
        data.append([
            idx, tc_obj.file_name, tc_obj.name, tc_obj.description
        ])
    print(tabulate(data, headers=['Id', 'File', 'TestCase', 'Description']))


def run_test_case_files(test_case_files: List[TestCaseFile], run_log_dir: str = ""):
    start_time = datetime.datetime.now()
    if not run_log_dir:
        run_log_dir = os.path.join('logs', start_time.strftime('%Y-%m-%d-%H-%M-%S'))
    run_log_dir = os.path.abspath(run_log_dir)
    for tc_file in test_case_files:
        run_test_case_file(tc_file, run_log_dir)
    end_time = datetime.datetime.now()
    Report(test_case_files, run_log_dir, start_time, end_time)
    print(f"\n====Logs {run_log_dir}====\n")


def run_test_case_file(tc_file: TestCaseFile, run_log_dir: str):
    # create a subdir for the tc file (module) under run_log_dir
    tc_file_log_dir = os.path.join(
        run_log_dir, inspect.getmodulename(tc_file.file_name))
    # if the framework has test_module_setup, test_case_setup (and cleanup)
    # inform the tc_file about that
    if getattr(framework, 'framework_module_setup'):
        tc_file.framework_module_setup = TestCase(framework.framework_module_setup)
    if getattr(framework, 'framework_module_cleanup'):
        tc_file.framework_module_cleanup = TestCase(framework.framework_module_cleanup)
    if getattr(framework, 'framework_case_setup'):
        tc_file.framework_case_setup = TestCase(framework.framework_case_setup)
    if getattr(framework, 'framework_case_cleanup'):
        tc_file.framework_case_cleanup = TestCase(framework.framework_case_cleanup)
    tc_file.run_test_cases(tc_file_log_dir)


def main():
    parser, args, tc_args = parse_args()
    test_case_files: List[TestCaseFile] = load_test_case_files(args.file_list)
    parse_test_case_args(test_case_files, tc_args)
    if args.list:
        print_testcases(test_case_files)
    elif args.help:
        print_help(parser, test_case_files)
    else:
        run_test_case_files(test_case_files, args.logdir)


if __name__ == "__main__":
    main()
