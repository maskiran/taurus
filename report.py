import datetime
import json
import os
from typing import List

from tabulate import tabulate

from testcase import TestCase
from testcase_file import TestCaseFile


def test_case_to_json(o: TestCase):
    return o.to_json()


class Report:
    def __init__(self, test_case_files: List[TestCaseFile], log_dir: str,
                 start_time: datetime, end_time: datetime):
        self.test_case_files: List[TestCaseFile] = test_case_files
        self.log_dir = log_dir
        self.start_time: datetime.datetime = start_time
        self.end_time: datetime.datetime = end_time
        self.duration = (end_time - start_time).total_seconds()
        self.total: int = 0
        self.passed: int = 0
        self.failed: int = 0
        self.failed_test_cases: List[TestCase] = []
        self.generate_stats()
        self.generate_json_report()
        self.generate_summary()

    def generate_stats(self):
        for tc_file in self.test_case_files:
            for tc in tc_file.get_test_cases():
                self.total += 1
                if tc.status == 'passed':
                    self.passed += 1
                else:
                    self.failed += 1
                    self.failed_test_cases.append(tc)

    def generate_json_report(self):
        json_file_name: str = os.path.join(self.log_dir, 'report.json')
        with open(json_file_name, 'w') as fd:
            data = {
                'summary': {
                    'total': self.total,
                    'passed': self.passed,
                    'failed': self.failed,
                    'start_time': str(self.start_time),
                    'end_time': str(self.end_time),
                    'duration': self.duration,
                    'log_dir': self.log_dir
                },
                'test_case_files': self.test_case_files
            }
            json.dump(data, fd, default=test_case_to_json, indent=4)

    def generate_summary(self):
        data = f"Total: {self.total}, Passed: {self.passed}, Failed: {self.failed}\n"
        data += f"Start Time: {self.start_time}, End Time: {self.end_time}\n"
        data += f"Duration: {self.duration} secs\n\n"
        data += "Failed Test Cases:\n"
        ftc_data = []
        for ftc in self.failed_test_cases:
            ftc_data.append([ftc.full_name, ftc.error])
        data += tabulate(ftc_data, tablefmt="grid")
        summary_file = os.path.join(self.log_dir, 'summary.txt')
        with open(summary_file, 'w') as fd:
            fd.write(data)
        print("\nExecution Summary")
        print("-----------------")
        print(data)
