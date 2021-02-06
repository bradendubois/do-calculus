

class OutputLogger:

    def __init__(self, print_result=False, print_detail=False, log=False, log_fd=None):
        """
        Create an instance of an OutputLogger, which can print to standard out, or log to a file.
        @param print_result: bool; whether or not to print final results from queries.
        @param print_detail: bool; whether or not to print computation steps.
        @param log: bool; whether or not to log a message to file.
        @param log_fd: an optional open file descriptor that can be written to.
        """
        self._print_result = print_result
        self._print_detail = print_detail
        self._log = log
        self._log_fd = log_fd

    ###########################################
    #        Set Print/Logging Details        #
    ###########################################

    def set_print_result(self, print_result: bool):
        self._print_result = print_result

    def set_print_detail(self, print_detail: bool):
        self._print_detail = print_detail

    def set_log(self, log: bool):
        self._log = log

    def set_log_fd(self, fd):
        self._log_fd = fd

    ###########################################
    #               Print / Log               #
    ###########################################

    def result(self, msg: str):
        if self._print_result:
            print(msg)
        self.log(msg)

    def detail(self, msg: str):
        if self._print_detail:
            print(msg)
        self.log(msg)

    def log(self, msg: str):
        if not self._log or not self._log_fd:
            return

        self._log_fd.write(msg + "\n")
