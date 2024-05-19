# Libraries description

## Task (crontask.py)

This class define the structure of a task with relatives getters and setters.

## Dbhandler (db_handler.py)

All db management goes here

## Logger (logger.py)

Log handler to simplify writing logs

Sample usage:

```python
from libs.logger import logger

logger = logger('name_show_in_log')

logger.msg(level='info', text='Information message')
logger.msg(level='warning', text='Warning message')
logger.msg(level='error', text='Error message')
...
```
