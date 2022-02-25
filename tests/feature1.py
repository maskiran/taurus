import random
import time


def parse_args(parser):
    parser.add_argument(
        '-n', '--num', help='Max random seconds to sleep', default=4, type=int)


def test_module_setup(tc):
    tc.logger.info(tc.framework_module_setup_output)
    # raise Exception("module setup error")
    return {'test module setup': 'tc-mod'}


def test_module_cleanup(tc):
    # raise Exception("module cleanup error")
    pass


def test_case_setup(tc):
    tc.logger.info(tc.framework_module_setup_output)
    tc.logger.info(tc.test_module_setup_output)
    tc.logger.info(tc.framework_case_setup_output)
    # raise Exception("module's case setup error")
    return {'test case setup': 'tc-test'}


def test_case_cleanup(tc):
    # raise Exception("module's case cleanup error")
    pass


def test_case1(tc):
    """
    Basic sanity test
    """
    tc.logger.info(tc.framework_module_setup_output)
    tc.logger.info(tc.test_module_setup_output)
    tc.logger.info(tc.framework_case_setup_output)
    tc.logger.info(tc.test_case_setup_output)
    tc.logger.info(f"Args: {tc.args}")
    tc.logger.info('Dump the contents of file a')
    with open('a') as fd:
        tc.logger.info(fd.read())
    tc.logger.info(f'Sleeping randomly between 1 and {tc.args.num} seconds')
    s = random.randint(1, tc.args.num)
    tc.logger.info(f'Sleeping {s} seconds')
    # time.sleep(s)
    _check_sum(1, 2, 3)


def test_case2(tc):
    """
    Basic sanity test 2
    """
    tc.logger.info('Checking if 2+3 is 5')
    tc.logger.info(f'Sleeping randomly between 1 and {tc.args.num} seconds')
    s = random.randint(1, tc.args.num)
    tc.logger.info(f'Sleeping {s} seconds')
    # time.sleep(s)
    _check_sum(2, 3, 4)


def _check_sum(x, y, t):
    assert x + y == t
