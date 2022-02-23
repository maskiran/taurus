def parse_args(parser):
    parser.add_argument('-m', '--num2', help='Number of requests')


def test_case1(tc):
    """
    Basic sanity test
    """
    tc.logger.info('Checking if 1*2 is 2')
    tc.logger.info(f"Args: {tc.args}")
    _check_product(1, 2, 2)


def test_case2(tc):
    """
    Basic sanity test
    """
    tc.logger.info('Checking if 2*2 is 4')
    _check_product(2, 2, 1)


def _check_product(x, y, p):
    assert x*y == p
