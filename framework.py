"""
All the framework related initializations are handled here. A team 
can define a set of actions to take before running a script/test case
and another set of actions at the end of the test case or script.
These could be a topology initialization at the start, collecting
logs/cores at the end and so on. The team can define how the topology
can be provided by the user (either through the test case or CLI param).
The runner (run.py) checks if the framework defines any module init/cleanup
and test case init/cleanup functions and makes those calls.
(Runner already calls these functions if they are defined at the test case
file, but the team may want to move those into the custom framework so each
individual user does not have to define in each of the files.)
"""

from argparse import ArgumentParser

from testcase import TestCase


def parse_args(parser: ArgumentParser):
    parser.add_argument('--topology', help='Framework level topology')


def framework_module_setup(tc: TestCase):
    tc.logger.info('framework module args %s', tc.args)
    return {'framework module setup': 'fm-mod'}


def framework_module_cleanup(tc: TestCase):
    return


def framework_case_setup(tc: TestCase):
    tc.logger.info(tc.framework_module_setup_output)
    tc.logger.info(tc.test_module_setup_output)
    return {'framework case setup': 'fm-test'}


def framework_case_cleanup(tc: TestCase):
    return
