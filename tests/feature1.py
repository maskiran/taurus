def parse_args(parser):
    parser.add_argument('-n', '--num', help='Number of requests')


def test_module_setup(tc):
    tc.logger.info(tc.framework_module_setup_output)
    return {'test module setup': 'tc-mod'}


def test_module_cleanup(tc):
    pass


def test_case_setup(tc):
    tc.logger.info(tc.framework_module_setup_output)
    tc.logger.info(tc.test_module_setup_output)
    tc.logger.info(tc.framework_case_setup_output)
    return {'test case setup': 'tc-case'}


def test_case_cleanup(tc):
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
    _check_sum(1, 2, 3)


def test_case2(tc):
    """
    Basic sanity test 2
    """
    tc.logger.info('Checking if 2+3 is 5')
    _check_sum(2, 3, 4)


def _check_sum(x, y, t):
    assert x+y == t
