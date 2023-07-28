```
$ python3.10 -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

```
$ python main.py
$ monkeytype stub lib
from valuetypes import (
    int16,
    int8,
)


def bar(x: int8) -> int8: ...


def foo(x: int8) -> int16: ...
$
```
