# Getting Started

```
git clone https://github.com/maskiran/taurus.git
cd taurus
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

# Test case file

Create a test case file **addition.py**. Create a function that defines your test case. The function name **must** start with **test_**. The function takes an argument, conventionally called *tc*. 

```python
def test_check_addition(tc):
    pass
```

# Run the Test case file

```
python run.py addition.py
```

This runs the all the functions whose names start with *test_*. A summary is provided on the stdout. A logs directory is created and inside that a subdirectory with the current timestamp. Under that the directory for the test case file name. Inside this directory there are logs for the test case.

```
$ ls -l logs
total 0
drwxr-xr-x  5 kiran  staff  160 Feb 26 10:46 2022-02-26-10-46-10
drwxr-xr-x  5 kiran  staff  160 Feb 26 10:46 2022-02-26-10-46-11
lrwxr-xr-x  1 kiran  staff   19 Feb 26 10:46 latest -> 2022-02-26-10-46-11

$ ls -l logs/latest/
total 16
drwxr-xr-x  5 kiran  staff   160 Feb 26 10:46 addition
-rw-r--r--  1 kiran  staff  1482 Feb 26 10:46 report.json
-rw-r--r--  1 kiran  staff   280 Feb 26 10:46 summary.txt

$ ls -l logs/latest/addition
total 24
-rw-r--r--  1 kiran  staff  383 Feb 26 10:46 framework_module_cleanup
-rw-r--r--  1 kiran  staff  375 Feb 26 10:46 framework_module_setup
-rw-r--r--  1 kiran  staff  931 Feb 26 10:46 test_check_addition
```

Ignore the other files in the *logs/latest/addition* and just look at *logs/latest/addition/test_check_addition*
and go through the log.

# Add more content to the test case
Our test_check_addition does not do anything yet. Let's enhance it. Our test case checks that 2 + 2 is 4. We will log what we are going to do.

The **tc** parameter provided to every test case is an instance of the **TestCase** object provided by the system. To get type hints in your editor for this object import the test case module. Look at this [document](test_case_object.md) for the details of all the properties/members of this object. For now we will use the *logger* member for logging. This is python standard *logging.Logger* instance provided by the system. This is set to DEBUG level. So you can use `tc.logger.info(message)` to log any messages.

```python
# importing this for type hints only and not mandatory
from testcase import TestCase


def test_check_addition(tc: TestCase):
    tc.logger.info("Check that 2+2 is 4")
    assert 2 + 2 == 4
```

Take a look at the log file **logs/latest/addition/test_check_addtion** and see the contents. Notice the log statements that were added in the test case function. When the test case completes without raising an exception, then it is considered as **passed**. To make a test case fail you need to raise an exception: either explicitly or implicitly.

Look at the other files in the logs. A *summary* and a *report,json* is generated in the top level directory. *summary* is a text file showing the main summary including stats and all the failed cases. *report.json* gives a json file of all the details. Take a look at these files. You can use the json file to store the contents in a database or any other test case management system.

# Fail Test case
Let us add a new test case that is going to fail. Add a new function to the addition.py

```python
def test_addition_fail(tc):
    tc.logger.info("Check that 3 + 2 is 5")
    assert 2 + 3 == 20
```

```
python run.py addition.py
```

This run fails one test case. Look at the logs directory and notice that there are 2 log files: 1 for each of the test cases. Again take a look at the summary, report.json for more details.

[Next - Test Module Customization](test_module.md)