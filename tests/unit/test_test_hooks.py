"""Unit tests for add_test_hook."""
import contextlib

import pytest

from RLTest import add_test_hook
from RLTest import test_hooks
from RLTest.test_hooks import run_with_hooks


@pytest.fixture(autouse=True)
def no_hooks():
    saved = list(test_hooks._hooks)
    del test_hooks._hooks[:]
    yield
    test_hooks._hooks[:] = saved


def recorder(log, name):
    @contextlib.contextmanager
    def hook(env, test):
        log.append((name, 'enter', env))
        yield
        log.append((name, 'exit', env))
    return hook


def test_no_hooks_runs_the_test():
    assert run_with_hooks(lambda env: env * 2, 21) == 42


def test_hooks_wrap_the_test_in_order():
    log = []
    add_test_hook(recorder(log, 'a'))
    add_test_hook(recorder(log, 'b'))
    run_with_hooks(lambda env: log.append(('test', env)), 'env')
    assert log == [('a', 'enter', 'env'), ('b', 'enter', 'env'), ('test', 'env'),
                   ('b', 'exit', 'env'), ('a', 'exit', 'env')]


def test_adding_a_hook_twice_runs_it_once():
    log = []
    hook = recorder(log, 'a')
    add_test_hook(hook)
    add_test_hook(hook)
    run_with_hooks(lambda env: None, 'env')
    assert log == [('a', 'enter', 'env'), ('a', 'exit', 'env')]


def test_a_failing_test_still_exits_the_hooks():
    log = []
    add_test_hook(recorder(log, 'a'))

    def failing(env):
        raise ValueError('boom')

    with pytest.raises(ValueError, match='boom'):
        run_with_hooks(failing, 'env')
    assert log == [('a', 'enter', 'env')]  # a contextmanager hook sees the exception


def test_a_hook_error_fails_the_test():
    @contextlib.contextmanager
    def check(env, test):
        yield
        raise AssertionError('hook check failed')

    add_test_hook(check)
    with pytest.raises(AssertionError, match='hook check failed'):
        run_with_hooks(lambda env: None, 'env')


def test_a_hook_gets_the_test_function():
    seen = []

    @contextlib.contextmanager
    def hook(env, test):
        seen.append(getattr(test, 'marker', None))
        yield

    def marked(env):
        pass
    marked.marker = 'skip-check'

    add_test_hook(hook)
    run_with_hooks(marked, 'env')
    assert seen == ['skip-check']
