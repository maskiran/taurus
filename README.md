# Test Case Management and Automation Infrastructure

```
git clone https://github.com/maskiran/taurus.git
cd taurus
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

# Write a test case
Open a file *addition.py*

```python
def test_check_addition(tc):
    tc.logger.info("Check that sum is correct")
    assert 1 + 2 == 3


def test_check_addition_identity(tc):
    tc.logger.info("Check that 0 is the identity")
    assert 3 + 0 == 0
```

# Run test cases
```
python run.py feature1.py
```

Look at the Documentation for more details

* [Getting Started](docs/getting-started.md)
* [Test Case Module - Hooks for  Test Case Developer](docs/test_module.md)
* [Framework Customization - Hooks for Automation Framework Developer](docs/framework.md)
* [Test Case Object Properties/Members](docs/test_case_object.md)