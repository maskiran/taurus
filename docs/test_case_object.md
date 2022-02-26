# Properties/Member of tc object

Every test case that you write must be defined as a function that starts with **test_** and must accept one parameter. The taurus engine creates an instance of object *TestCase* object and passes that to the function when it is executed. Here are the members/properties of the **tc** object

## Test Case (tc) Object Properties
* `file_name` - The full path of the test case file where the function is defined
* `module_name` - The last part of the file name without py extension (inspect.getmodulename(file_name))
* `name` - Test case function name (e.g test_check_addition) that's being executed
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
* `args` - CLI Parameters passed while running the test ([Details](test_module.md))
* `framework_module_setup_output` - Output of the framework module setup ([Details](framework.md))
* `test_module_setup_output` - Output of the test module set ([Details](test_module.md))
* `framework_case_setup_output` - Output of the framework module setup ([Details](framework.md))
* `test_case_setup_output` - Output of the test module set ([Details](test_module.md))