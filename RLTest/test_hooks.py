"""Hooks that run around each function test that takes an ``env``."""
import contextlib

_hooks = []


def add_test_hook(hook):
    """
    Run ``hook(env, test)`` around every function test that takes an
    ``env``; ``test`` is the test function, so a hook can honour markers set
    on it.

    ``hook`` returns a context manager, such as a generator decorated with
    ``contextlib.contextmanager``: it is entered before the test and exited
    after it. Failed assertions and exceptions in the hook fail the test, as
    the test's own would. Hooks run in the order added; adding one again does
    nothing.
    """
    if hook not in _hooks:
        _hooks.append(hook)


def run_with_hooks(target, env):
    with contextlib.ExitStack() as stack:
        for hook in list(_hooks):
            stack.enter_context(hook(env, target))
        return target(env)
