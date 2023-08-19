# debounce.py

from time import sleep
from metacogitor.utils import debounce


def test_debounce_delays_function_execution():
    counter = 0

    @debounce(wait=1)
    def increment():
        nonlocal counter
        counter += 1

    increment()  # First call allowed
    increment()  # Call again before timeout
    assert counter == 1

    sleep(1.1)  # Wait for timeout
    increment()  # Call again after timeout
    assert counter == 2


def test_debounce_allows_immediate_first_call():
    counter = 0

    @debounce(wait=1)
    def increment():
        nonlocal counter
        counter += 1

    increment()
    assert counter == 1


def test_debounce_subsequent_rapid_calls_delayed():
    counter = 0

    @debounce(wait=1)
    def increment():
        nonlocal counter
        counter += 1

    increment()
    increment()
    increment()

    sleep(0.5)
    assert counter == 1

    sleep(0.6)
    increment()
    assert counter == 2


def test_debounced_function_return_value():
    @debounce(wait=0.1)
    def add(a, b):
        return a + b

    res = add(1, 2)
    assert res == 3  # Correct return value


def test_debounced_as_function():
    counter = 0

    def increment():
        nonlocal counter
        counter += 1

    db_increment = debounce(increment, wait=1)

    db_increment()
    assert counter == 1

    db_increment()
    db_increment()
    assert counter == 1

    sleep(1.1)
    db_increment()
    assert counter == 2
