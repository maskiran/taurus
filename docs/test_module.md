# Test Case File (Test Module) Customization

The test case file (or test module) defines all the test cases (test_<function_name>). There are other special functions that can defined in this file. 

# Test Case Parameters
When you write a test case, you may want to pass in parameters during the run time from the CLI. Define a function 

```python
def parse_args(parser)
    pass
```

The parser is the python standard **argparse.ArgumentParser** instance. You can add parameters using [parser.add_argument](https://docs.python.org/3/library/argparse.html#the-add-argument-method)

You may write a test case that might be required to run for a given time period or certain number of iterations, or a test parameters file to login to the databases etc. 

Let's write a test case that runs a given number of iterations with a default value. Write the following in a file *scale.py*

```python
from argparse import ArgumentParser
import os

from testcase import TestCase


def parse_args(parser: ArgumentParser):
    parser.add_argument('-c', '--count', type=int, default=2,
                        help='Number of iterations')


def test_run_date(tc: TestCase):
    """
    Run date command for the given number of times
    """
    for i in range(tc.args.count):
        tc.logger.info(f"Running date command for {i+1} time")
        os.system('date')
```

# Check Help
```
python run.py scale.py -h
Runner Help

positional arguments:
  file_list             Test Case files, multiple files can be provided

optional arguments:
  -d LOGDIR, --logdir LOGDIR
                        Log directory (default $PWD/logs/<current-timestamp>)
  -l, --list            Print test case names
  -h, --help            Help Message

Parameters of Test Case /home/centos/taurus/scale.py

optional arguments:
  -c COUNT, --count COUNT
                        Number of iterations
```

Look at the parameters and see that the parameters defined in the test case are shown in the help

# Run with parameters

```
# default parameter
python run.py scale.py

# override the default value
python run.py scale.py -c 5
```

The first run is done with default parameter value (of 2) and 2nd one with overridden parameter of 5. Check the logs and see that the command is run the given number of times appropriately

The parameters are defined at a module (test case file) level. So all the test case functions in the same file have access to parameters

# Test Module Setup (Init/Setup function for the whole module)
This function is used to run a init/setup function **once** before running any test cases. This could used to do an initialization, like installing packages, or setting up a topology. The output of the module setup function is available to all the test case functions as **tc.test_module_setup_output**

Define the function as:

```python
def test_module_setup(tc: TestCase):
    return "output"
```

As an example, we will create a temp directory and let other test cases use this directory, for eg. to store some content, which can also be accessed by the test functions that follow. This can be used to achieve inter test case data transfer.

Create a file scale.py and put the following content

```python
import tempfile
from testcase import TestCase


def test_module_setup(tc: TestCase):
    """
    Create a temporary directory that can be accessed by all the test cases
    """
    tdir = tempfile.mkdtemp()
    tc.logger.info(f'Created a temporary directory {tdir}')
    return tdir


def test_case1(tc: TestCase):
    tc.logger.info(f"Output of module_setup {tc.test_module_setup_output}")
    tc.logger.info("Create a temporary file in the above directory")
    tfile = tempfile.mkstemp(dir=tc.test_module_setup_output)
    tc.logger.info(f"Created {tfile[1]} in {tc.test_module_setup_output} directory")
    return tfile[1]
```

```
python run.py scale.py
```

Check the logs to find the temp directories and files created created. test_module_setup is executed as anothe test case. So it has its own log file in the logs directory.

# Test Module Cleanup (Final/Cleanup function for the whole module)
Just like a function is provided to do a module level setup, cleanup function is also available to do a module level cleanup. This is run once at the end of all the test cases in the module (test case file). This function can access the output of test_module_setup just like any other test case.

Define the function as:

```python
def test_module_cleanup(tc: TestCase):
    # do something with tc.test_module_setup_output
    return
```

Following the example, we will enhance it to delete the directory created by the test_setup_module

```python
import os
import shutil
import tempfile
from testcase import TestCase


def test_module_setup(tc: TestCase):
    """
    Create a temporary directory that can be accessed by all the test cases
    """
    tdir = tempfile.mkdtemp()
    tc.logger.info(f'Created a temporary directory {tdir}')
    return tdir


def test_case1(tc: TestCase):
    tc.logger.info(f"Output of module_setup {tc.test_module_setup_output}")
    tc.logger.info("Create a temporary file in the above directory")
    tfile = tempfile.mkstemp(dir=tc.test_module_setup_output)
    tc.logger.info(f"Created {tfile[1]} in {tc.test_module_setup_output} directory")
    return tfile[1]

def test_module_cleanup(tc: TestCase):
    """
    Delete the temporary directory (and all its contents) that was created by the test_module_setup
    """
    tc.logger.info(f"Check that the directory exists {tc.test_module_setup_output}")
    if os.path.exists(tc.test_module_setup_output):
        tc.logger.info("Directory exists")
    tc.logger.info(f"Delete the directory {tc.test_module_setup_output} created by the setup")
    shutil.rmtree(tc.test_module_setup_output, ignore_errors=True)
    tc.logger.info("Check that the directory is gone")
    assert os.path.exists(tc.test_module_setup_output) != True, f"Directory is still present"
```

```
python run.py scale.py
```

# Test Case Setup (function to run at the start of every test case)
Just like module setup that runs at the start of module (once), a function can be provided that runs at the start of **every** test case. Instead of the developer calling this function explicitly in the code, taurus engine takes care of this call. 

Define the function as:

```python
def test_case_setup(tc: TestCase):
    return "output"
```

From the previous example, the test case would create a temp file in the directory created by the module_setup. Move this code (creation of the temp file) from the test case into the test setup. (This assumes that every test case needs a temporary file). The output of the test case setup is accessible to the test case as **tc.test_case_setup_output**

```python
import tempfile
import os
import shutil
from testcase import TestCase


def test_module_setup(tc: TestCase):
    """
    Create a temporary directory that can be accessed by all the test cases
    """
    tdir = tempfile.mkdtemp()
    tc.logger.info(f'Created a temporary directory {tdir}')
    return tdir


def test_case_setup(tc: TestCase):
    """
    Create a temporary file that can be used by the test case
    """
    tc.logger.info(f"Output of module_setup {tc.test_module_setup_output}")
    tc.logger.info("Create a temporary file in the above directory")
    tfile = tempfile.mkstemp(dir=tc.test_module_setup_output)
    tc.logger.info(
        f"Created {tfile[1]} in {tc.test_module_setup_output} directory")
    return tfile[1]


def test_case1(tc: TestCase):
    tc.logger.info(
        f'Acting on the temp file created by setup {tc.test_case_setup_output}')


def test_case2(tc: TestCase):
    tc.logger.info(
        f'Acting on the temp file created by setup {tc.test_case_setup_output}')


def test_module_cleanup(tc: TestCase):
    """
    Delete the temporary directory (and all its contents) that was created by the test_module_setup
    """
    tc.logger.info(
        f"Check that the directory exists {tc.test_module_setup_output}")
    if os.path.exists(tc.test_module_setup_output):
        tc.logger.info("Directory exists")
    tc.logger.info(
        f"Delete the directory {tc.test_module_setup_output} created by the setup")
    shutil.rmtree(tc.test_module_setup_output, ignore_errors=True)
    tc.logger.info("Check that the directory is gone")
    assert os.path.exists(
        tc.test_module_setup_output) != True, f"Directory is still present"
```

```
python run.py scale.py
```

Look at the logs for test_case1 and test_case2 and see that both of those got a different temp file and the main test function code just acts on the file instead of creating it.

# Test Case Cleanup (function to run at the end of every test case)
Just like module cleanup that runs at the end of module (once), a function can be provided that runs at the end of **every** test case. Instead of the developer calling this function explicitly in the code, taurus engine takes care of this call. 

Define the function as:

```python
def test_case_cleanup(tc: TestCase):
    # do something with tc.test_case_setup_output
    pass
```

Following the above example, the temp file created by the test_case_setup, can be deleted at the end of the test case.

```python
import tempfile
import os
import shutil
from testcase import TestCase


def test_module_setup(tc: TestCase):
    """
    Create a temporary directory that can be accessed by all the test cases
    """
    tdir = tempfile.mkdtemp()
    tc.logger.info(f'Created a temporary directory {tdir}')
    return tdir


def test_case_setup(tc: TestCase):
    """
    Create a temporary file that can be used by the test case
    """
    tc.logger.info(f"Output of module_setup {tc.test_module_setup_output}")
    tc.logger.info("Create a temporary file in the above directory")
    tfile = tempfile.mkstemp(dir=tc.test_module_setup_output)
    tc.logger.info(
        f"Created {tfile[1]} in {tc.test_module_setup_output} directory")
    return tfile[1]


def test_case_cleanup(tc: TestCase):
    """
    Delete the temporary file that was created by the test case setup
    """
    tc.logger.info(
        f"Remove the temp file created by the test case setup {tc.test_case_setup_output}")
    os.remove(tc.test_case_setup_output)


def test_case1(tc: TestCase):
    tc.logger.info(
        f'Acting on the temp file created by setup {tc.test_case_setup_output}')


def test_case2(tc: TestCase):
    tc.logger.info(
        f'Acting on the temp file created by setup {tc.test_case_setup_output}')


def test_module_cleanup(tc: TestCase):
    """
    Delete the temporary directory (and all its contents) that was created by the test_module_setup
    """
    tc.logger.info(
        f"Check that the directory exists {tc.test_module_setup_output}")
    if os.path.exists(tc.test_module_setup_output):
        tc.logger.info("Directory exists")
    tc.logger.info(
        f"Delete the directory {tc.test_module_setup_output} created by the setup")
    shutil.rmtree(tc.test_module_setup_output, ignore_errors=True)
    tc.logger.info("Check that the directory is gone")
    assert os.path.exists(
        tc.test_module_setup_output) != True, f"Directory is still present"
```

# Summary

Hooks that can be used by the test case developer:

* function to run once at the start of the module - test_module_setup
* function run at the start of each test case - test_case_setup
* function run at the end of each test case - test_case_cleanup
* function to run once at the end of the module - test_module_cleanup

[Next - Framework Customization](framework.md)