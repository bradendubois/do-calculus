GREEN = '\033[92m'
FAIL = '\033[91m'
END = '\033[0m'


def print_test_result(success: bool, msg: str):
    """
    Print a test result to standard out, with a header marking the success of the test
    @param success: bool; True if the test was successful, False otherwise
    @param msg: string; Any arbitrary message returned by the test
    """
    color = GREEN if success else FAIL
    print(f"[{color}{'OK' if success else 'ERROR'}{END}]: {msg}")
