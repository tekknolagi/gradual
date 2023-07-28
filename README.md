```
$ python3.10 -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

```
$ python main.py
$ monkeytype stub lib
from typing import Union
from valuetypes import (
    int16,
    int8,
)


def bar(x: Union[str, int8]) -> Union[str, int8]: ...


def foo(x: int8) -> int16: ...


def nonint(x: str) -> str: ...
$
```
