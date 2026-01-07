"""Tests for pytest plugin markus_autotest_helpers_notebook/pytest/notebook_collector_plugin.py"""
import os.path


def test_plugin(pytester):
    pytester.makeconftest(
        """
        pytest_plugins = ['markus_autotest_helpers_notebook.pytest.notebook_collector_plugin']
        """
    )

    pytester.copy_example(os.path.join(os.path.dirname(__file__), 'fixtures/test.ipynb'))
    result = pytester.runpytest('test.ipynb')

    result.assert_outcomes(
        passed=3,
        failed=4
    )
