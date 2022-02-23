# Test Case Management and Automation Infrastructure

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py -h
```

## List Test Cases
```
python run.py -l <file1.py> <file2.py>
python run.py -t <file1.py> <file2.py>
```

## Run Test Cases
```
python run.py <file1.py> <file2.py>
```

## Writing Test Cases

1. Open a file (eg. feature1.py). This file can be located anywhere
1. Write a function with a prefix `test_` and one argument, conventionally called `tc`
    ```
    def test_check_prod_url_is_reachable(tc):
        tc.logger.info('Check that the production url is reachable')
    ```
1. If the function raises an exception, the test is considered **FAILED**
1. If the function runs successfully without errors, it is considered **PASSED**
1. The `tc` has properties (described below) provided by the framework

## Test Case (tc) Object Properties
* `file_name` - The full path of the test case file
* `module_name` - The last part of the file name without py extension
* `name` - Test case function name (e.g test_check_website) that's being executed
* `full_name` - module_name.name
* `description` - doc string of the test case function
* `function` - Function object of the current test case function
* `start_time` - Start time of the test case (datetime.datetime)
* `end_time` -  End time of the test case (datetime.datetime), updated at the end of the test
* `duration` - Total duration in seconds, updated at the end of the test
* `status` - Status of the test run, updated at the end of the test
* `error` - Error message if the test failed, updated at the end of the test
* `logger` - logging.getLogger instance, that can be used to log messages to the log file
* `log_dir` - Log directory where the log file for the current test case is located
* `log_file` - Full log file path/name for the current test case
* `mod_setup_output` - Output of the `test_module_setup` function (described below)
* `test_case_setup_ouput` - Output of the `test_case_setup` function (described below)
* `args` - CLI Parameters (described below)

## Init/Cleanup Functions

* `test_module_setup` - If the function is defined in the test case file, run once at the start of the test case file. The output of this function is available to the test case as `tc.mod_setup_output`
* `test_module_cleanup` - If the function is defined in the test case file, run once at the end of the test case file (after all the test cases in the file are executed)
* `test_case_setup` - If the function is defined in the test case file, run at the start of every test case. The output of this function is available to the test case as `tc.test_case_setup_output`
* `test_case_cleanup` - If the function is defined in the test case file, run at the end of every test case

```python
def test_module_setup(tc):
    tc.logger.info('module setup code goes here')
    return {'key': 'value'}

def test_module_cleanup(tc):
    tc.logger.info('module cleanup code goes here')

def test_case_setup(tc):
    tc.logger.info('test case setup code goes here')
    return {'key2': 'value2'}

def test_case_cleanup(tc):
    tc.logger.info('test case cleanup code goes here')
```

## Test Case Parameters
Test Case file can define its own cli parameters that can be passed from the CLI during execution. Define a function 
```
def parse_args(parser):
    parser.add_argument('-n', '--num', help='n help')
```

parser is an instance of the argparse.ArgumentParser. You can add as many arguments. The arguments are available to the test case as `tc.args`, e.g `tc.args.num`. `tc.args` is the parsed Namespace as a result of `parser.parser_args()` of the ArgumentParser. If multiple test cases define the same argument name, then the same value is passed to all the test case files.

## Management features coming soon