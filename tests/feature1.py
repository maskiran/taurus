def parse_args(parser):
    parser.add_argument('-n', '--num', help='Number of requests')


def test_module_setup(tc):
    tc.logger.info('Init of the feature1.py')
    return {'mod': 'hello'}


def test_module_cleanup(tc):
    tc.logger.info('Cleanup of the feature1.py')


def test_case_setup(tc):
    tc.logger.info('Init of the testcase.py')
    return {'test': 'kiran'}


def test_case_cleanup(tc):
    tc.logger.info('Cleanup of the testcase.py')


def test_case1(tc):
    """
    Basic sanity test
    """
    tc.logger.info('Checking if 1+2 is 3')
    tc.logger.info(tc.module_setup_output)
    tc.logger.info(tc.test_case_setup_output)
    tc.logger.info(f"Args: {tc.args}")
    tc.logger.info('Dump the contents of file a')
    with open('a') as fd:
        tc.logger.info(fd.read())
    _check_sum(1, 2, 3)


def test_case2(tc):
    """
    Basic sanity test 2
    """
    tc.logger.info('Checking if 2+3 is 5')
    _check_sum(2, 3, 4)


def _check_sum(x, y, t):
    assert x+y == t
