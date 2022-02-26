# Framework Customization

As a team or organization you can build an automation framework by using the customization capabilities built into taurus.

In the [Test Module](test_module.md) we looked into different ways a test case developer can customize: using the hooks:
* function to run once at the start of the module - test_module_setup
* function run at the start of each test case - test_case_setup
* function run at the end of each test case - test_case_cleanup
* function to run once at the end of the module - test_module_cleanup

As a framework (automation engine) developer for your team, you have similar hooks available for customization. When you use these hooks, it applies to all the test cases and modules. As a team you may want to perform some action at the start of each test case or module that you don't want to ask the test developer to put into their code. For example, you may want to check the logs on a device or application or check for any crashes or cores at the end of each test case. Instead of asking the developer to do these actions, you can perform these using the framework hooks.

Once you cloned the repository, there is a framework.py available to you. It has functions that sound similar to the test_module functions.

* parse_args - Framework specific cli args
* framework_module_setup - Like test_module_setup, this function is run before the test_module_setup. This function also has access to the test_case module that's going to be run. So you can ask all the developers to put a variable in their test case files and then framework can use that to "do something" with that variable. For example, you can request test case developers to always have a variable for the APP_NAME or DUT_TOPOLOGY. You can then read that and setup the app or dut topology.
* framework_case_setup - This is similar to test_case_setup but runs before that
* framework_case_cleanup - Similar to test_case_cleanup, runs after that
* framework_module_cleanup - Similar to test_module_cleanup and runs at the end of the module

Here is a flow of the different functions and the parameters 

```
framework_parse_args(parser: argparse.ArgumentParser)
framework_module_setup(tc: TestCase, test_case_file_module: ModuleType)
test_module_setup(tc: TestCase)

foreach test case:
    framework_case_setup(tc: TestCase)
    test_case_setup(tc: TestCase)
    test_case(tc: TestCase)
    test_case_cleanup(tc: TestCase)
    framework_case_cleanup(tc: TestCase)
endfor

test_module_cleanup(tc: TestCase)
framework_module_cleanup(tc: TestCase)
```

The output of the functions are accessible to the test cases and cleanup functions

* framework_module_setup output accessible as framework_module_setup_output
* framework_case_setup output accessible as framework_case_setup_output