class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_test_result(success: bool, msg: str):
    """
    Print a test result to standard out, with a header marking the success of the test
    @param success: bool; True if the test was successful, False otherwise
    @param msg: string; Any arbitrary message returned by the test
    """
    color = bcolors.OKGREEN if success else bcolors.WARNING
    print(f"[{color}{success}{bcolors.ENDC}]: {msg}")
