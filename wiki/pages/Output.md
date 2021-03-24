Control over the output that is printed to standard output from usage of the [[API|Do API]].

Here, we will make clear *two* categorizations of output:
1. **Result**: the final result returned from some computation
2. **Detail**: any intermediate information involved in some computation

## Print Result

Set whether to print the result of an API call to standard output. 

STUB|set_print_result

### Example

```python
from do.API import Do

do_api = Do("models/model1.yml")

do_api.set_print_result(True)

# queries here...
```

## Print Detail

Set whether to print the detail of an API call to standard output.

STUB|set_print_detail

### Example

```python
from do.API import Do

do_api = Do("models/model1.yml")
do_api.set_print_detail(True)

# queries here...
```

## Set Logging

Set whether to log results and details to some file descriptor.

Requires a file descriptor to have been set when [[instantiating the API|Loading a Model]], or [explicitly set](#set-log-fd). 

STUB|set_logging

### Example

```python
from pathlib import Path
from do.API import Do


file = Path("output/model1-output")
f = file.open("w")

do_api = Do("models/model1.yml", log_fd=f)

do_api.set_logging(True)

# queries here...

f.close()
```

**Important**
- If logging is enabled, What is written to the file descriptor set will be all results and details will be written to the file, regardless of settings for whether to *print* results and/or details.

## Set Log FD

Set an open file descriptor as the file descriptor to write to.

STUB|set_log_fd

### Example

```python
from pathlib import Path
from do.API import Do

do_api = Do("models/model1.yml")

file = Path("output/model1-output")
f = file.open("w")

do_api.set_log_fd(f)

# queries here...

f.close()
```

**Important**
- For this, *any* open file descriptor can be given, as long the file descriptor object given *has write permission*, and supports a ``.write()`` method that **takes a string as input**.
