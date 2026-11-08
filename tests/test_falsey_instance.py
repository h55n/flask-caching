import pytest

from flask_caching.utils import function_namespace


@pytest.mark.parametrize("truth_method", ["__bool__", "__len__"])
def test_falsey_bound_method_namespace(truth_method):
    class Falsey:
        def __bool__(self):
            return False

        def value(self):
            return 1

    if truth_method == "__len__":
        del Falsey.__bool__
        Falsey.__len__ = lambda self: 0
    instance = Falsey()
    assert function_namespace(instance.value)[1] is not None


@pytest.mark.parametrize("truth_method", ["__bool__", "__len__"])
@pytest.mark.parametrize("delete_version", [False, True])
def test_delete_memoized_falsey_instance_only_invalidates_that_instance(
    app, cache, truth_method, delete_version
):
    class Falsey:
        def __init__(self):
            self.calls = 0

        def __bool__(self):
            return False

        @cache.memoize()
        def value(self, argument):
            self.calls += 1
            return self.calls

    if truth_method == "__len__":
        del Falsey.__bool__
        Falsey.__len__ = lambda self: 0
    first, second = Falsey(), Falsey()
    with app.test_request_context():
        assert first.value(3) == second.value(3) == 1
        if delete_version:
            cache.delete_memoized_verhash(first.value)
        else:
            cache.delete_memoized(first.value)
        assert first.value(3) == 2
        assert second.value(3) == 1
