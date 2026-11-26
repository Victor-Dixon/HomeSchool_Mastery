"""Isolate app factory startup and supply explicit test-only bootstrap credentials."""
import pytest
from flask import Flask


@pytest.fixture(scope="session", autouse=True)
def isolated_bootstrap(tmp_path_factory):
    instance = tmp_path_factory.mktemp("factory-instance")
    original = Flask.__init__
    def isolated_init(self, *args, **kwargs):
        kwargs.setdefault("instance_path", str(instance))
        original(self, *args, **kwargs)

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(Flask, "__init__", isolated_init)
        for name in ("ADMIN", "CHARLIE", "CHRIS"):
            mp.setenv("HOMESCHOOL_BOOTSTRAP_" + name + "_PASSWORD",
                      "isolated-fixture-" + name.lower() + "-only")
        yield
