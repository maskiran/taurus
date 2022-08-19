# Getting Started

```
git clone https://github.com/maskiran/taurus.git
cd taurus
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

# Test case file

Create a test case file `addition.py`. Create a function that defines your test case. The function name **must** start with **test_**. The function takes an argument, conventionally called *tc*. 

```python
def test_check_addition(tc):
    pass
```

# Run the Test case file

```
python run.py addition.py
```

This runs the all the functions whose names start with *test_*. A summary is provided on the stdout. `logs` directory with a time stamped folder of the current run is created

```
$ tree logs
logs
|-- 2022-08-18-18-39-21
|   |-- addition
|   |   |-- framework_module_cleanup
|   |   |-- framework_module_setup
|   |   |-- test_check_addition
|   |   `-- test_check_addition_identity
|   |-- report.json
|   `-- summary.txt
`-- latest -> 2022-08-18-18-39-21
```

# Add more content to the test case
Modify the test case function to check that 2 + 2 is 4.

The **tc** parameter provided to every test case is an instance of the **TestCase** object provided by the system. To get type hints in your editor for this object import the test case module. Look at this [document](test_case_object.md) for the details of all the properties/members of this object. For now we will use the *logger* member for logging. This is python standard *logging.Logger* instance provided by the system. This is set to DEBUG level. So you can use `tc.logger.info(message)` to log any messages.

```python
# import this for type hints only and not mandatory
from testcase import TestCase


def test_check_addition(tc: TestCase):
    tc.logger.info("Check that 2+2 is 4")
    assert 2 + 2 == 4
```

Take a look at the log file **logs/latest/addition/test_check_addtion** and see the contents. Notice the log statements that were added in the test case function. When the test case completes without raising an exception, it is considered as **passed**. To make a test case fail you need to raise an exception: either explicitly or implicitly.

A *summary* and a *report,json* is generated in the top level directory. *summary* is a text file showing the main summary including stats and all the failed cases. *report.json* gives a json file of all the details. You can use the json file to store the contents in a database or any other test case management system.

# Fail Test case
Add a new test case that is going to fail.

```python
def test_addition_fail(tc):
    tc.logger.info("Check that 2 + 3 is 5")
    assert 2 + 3 == 20
```

```
python run.py addition.py
```

This run fails one test case. Look at the logs directory and notice that there are 2 log files: 1 for each of the test cases

[Next - Test Module Customization](test_module.md)