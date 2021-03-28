def print_test_result(success: bool, msg: str):
    """
    Print a test result to standard out, with a header marking the success of the test
    @param success: bool; True if the test was successful, False otherwise
    @param msg: string; Any arbitrary message returned by the test
    """
    green = '\033[92m'
    fail = '\033[91m'
    end = '\033[0m'

    color = green if success else fail
    print(f"[{color}{'OK' if success else 'ERROR'}{end}]: {msg}")
