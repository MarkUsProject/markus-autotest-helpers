import ast
import os

from markus_autotest_helpers_python.code_properties import is_unimplemented, get_recursive, \
    get_functions_using, get_functions_that_call, is_empty
import fixtures.example_code as example_code
import pytest
import inspect


def get_all_examples() -> list:
    """Return a list of all functions and methods in example_code"""
    all_examples = []

    for callable_name in [name for name in dir(example_code) if not name.startswith('__')]:
        callable_object = getattr(example_code, callable_name)

        if inspect.isclass(callable_object):
            # If the object is a class, add all of its methods instead
            for method_name in dir(callable_object):
                # FIXME: We ignore all special methods for this, as the example
                #        code does not implement any of these.
                if not method_name.startswith("_"):
                    all_examples.append(f"{callable_name}.{method_name}")
        else:
            all_examples.append(callable_name)

    return all_examples


EXAMPLES = get_all_examples()


@pytest.mark.parametrize('path_or_module', [
    os.path.join(os.path.dirname(__file__), 'fixtures', 'example_code.py'),
    example_code
], ids=[
    'path',
    'module'
])
class TestGetRecursive:
    """Tests for get_recursive.
    """

    @pytest.mark.parametrize('name', [
        name for name in EXAMPLES if 'recursive' in name
    ]
                             )
    def test_indirect_true(self, path_or_module, name) -> None:
        """Test that get_recursive() on example_code.py returns all of the
        recursive functions/methods when indirect=True.
        """
        recursives = get_recursive(path_or_module, indirect=True)
        assert name in recursives

    def test_excludes_non_recursive(self, path_or_module) -> None:
        """Test that get_recursive() on example_code.py does not return any
        functions that are not recursive when indirect=True.
        """
        recursives = get_recursive(path_or_module, indirect=False)
        assert all('recursive' in name for name in recursives)

    @pytest.mark.parametrize('name', [
        name for name in EXAMPLES if 'recursive_direct' in name
    ]
                             )
    def test_indirect_false(self, path_or_module, name) -> None:
        """Test that get_recursive() on example_code.py returns all of the
        directly recursive functions/methods when indirect=False.
        """
        recursives = get_recursive(path_or_module, indirect=False)
        assert name in recursives

    def test_indirect_false_excludes_indirects(self, path_or_module) -> None:
        """Test that get_recursive() on example_code.py does not return any
        functions with indirect in the name when indirect=False.
        """
        recursives = get_recursive(path_or_module, indirect=False)
        assert all('indirect' not in name for name in recursives)


@pytest.mark.parametrize('path_or_module', [
    os.path.join(os.path.dirname(__file__), 'fixtures', 'example_code.py'),
    example_code
], ids=[
    'path',
    'module'
])
class TestIsUnimplemented:
    """Tests for is_unimplemented
    """

    @pytest.mark.parametrize('function_name', [
        name for name in EXAMPLES if 'empty' in name
    ])
    def test_true_for_empty_given_name(self, path_or_module, function_name):
        """Test that is_unimplemented returns True for all of the empty
        functions when given a file path and the function name.
        """
        assert is_unimplemented(path_or_module, function_name=function_name)

    @pytest.mark.parametrize('function_name', [
        name for name in EXAMPLES if 'empty' in name and 'ExampleSubclass' not in name
    ])
    def test_true_for_empty_function(self, path_or_module, function_name):
        """Test that is_unimplemented returns True for all of the empty
        functions.

        Does *not* work when given a subclass but not the source of its parent.
        """
        tokens = function_name.split(".")
        if not isinstance(path_or_module, str):
            current = getattr(example_code, tokens[0])
        else:
            current = path_or_module

        if len(tokens) > 1:
            assert is_unimplemented(current, function_name=function_name)
        else:
            assert is_unimplemented(current)

    @pytest.mark.parametrize('function_name', [
        name for name in EXAMPLES if 'empty' not in name
    ])
    def test_false_for_nonempty(self, path_or_module, function_name):
        """Test that is_unimplemented returns False for all of the
        non-empty functions
        """
        assert is_unimplemented(path_or_module, function_name=function_name) is False


@pytest.mark.parametrize('path_or_module', [
    os.path.join(os.path.dirname(__file__), 'fixtures', 'example_code.py'),
    example_code
], ids=[
    'path',
    'module'
])
class TestIsEmpty:
    """Tests for is_empty
    """

    @pytest.mark.parametrize('function_name', [
        name for name in EXAMPLES if 'empty' in name
    ])
    def test_true_for_empty(self, path_or_module, function_name):
        """Test that is_empty returns True for all of the empty
        functions when given a file path and the function name.
        """
        assert is_unimplemented(path_or_module, function_name)

    @pytest.mark.parametrize('function_name', [
        name for name in EXAMPLES if 'empty' not in name
    ])
    def test_false_for_nonempty(self, path_or_module, function_name):
        """Test that is_empty returns False for all of the
        non-empty functions
        """
        assert is_empty(path_or_module, function_name) is False


@pytest.mark.parametrize('path_or_module', [
    os.path.join(os.path.dirname(__file__), 'fixtures', 'example_code.py'),
    example_code
], ids=[
    'path',
    'module'
])
class TestGetFunctionsUsing:
    """Tests for get_functions_using
    """

    @pytest.mark.parametrize('function_name', [
        name for name in EXAMPLES if 'for' in name
    ])
    def test_for(self, path_or_module, function_name):
        """Test that get_functions_using returns all of the functions that
        use a For-loop
        """
        assert function_name in get_functions_using(path_or_module, {ast.For})

    @pytest.mark.parametrize('function_name', [
        name for name in EXAMPLES if 'for' not in name
    ])
    def test_for_excludes_non_for_loops(self, path_or_module, function_name):
        """Test that get_functions_using returns none of the functions that
        do not use a For-loop
        """
        assert function_name not in get_functions_using(path_or_module, {ast.For})

    @pytest.mark.parametrize('function_name', [
        name for name in EXAMPLES if 'while' in name
    ])
    def test_while(self, path_or_module, function_name):
        """Test that get_functions_using returns all of the functions that
        use a While-loop
        """
        assert function_name in get_functions_using(path_or_module, {ast.While})

    @pytest.mark.parametrize('function_name', [
        name for name in EXAMPLES if 'while' not in name
    ])
    def test_for_excludes_non_while_loops(self, path_or_module, function_name):
        """Test that get_functions_using returns none of the functions that
        do not use a While-loop
        """
        assert function_name not in get_functions_using(path_or_module, {ast.While})

    @pytest.mark.parametrize('function_name', [
        name for name in EXAMPLES if 'while' in name or 'for' in name
    ])
    def test_loops(self, path_or_module, function_name):
        """Test that get_functions_using returns all functions with a
        for- or while- loops
        """
        assert function_name in get_functions_using(path_or_module,
                                                    {ast.While, ast.For})

    @pytest.mark.parametrize('function_name', [
        name for name in EXAMPLES if 'while' not in name and 'for' not in name
    ])
    def test_excludes_non_loops(self, path_or_module, function_name):
        """Test that get_functions_using returns no functions without a
        for- or while- loops
        """
        assert function_name not in get_functions_using(path_or_module,
                                                        {ast.While, ast.For})


@pytest.mark.parametrize('path_or_module', [
    os.path.join(os.path.dirname(__file__), 'fixtures', 'example_code.py'),
    example_code
], ids=[
    'path',
    'module'
])
class TestGetFunctionsThatCall:
    """Tests for get_functions_that_call
    """

    # FIXME: In code_properties, all methods are assumed to belong to
    #        the class that calls it (as the AST provides no information
    #        otherwise). As such, these tests would fail for method calls.
    # When fixed, remove the <and "." not in name> from the filter.
    @pytest.mark.parametrize('function_name', [
        name for name in EXAMPLES if 'sort_' in name and "." not in name
    ])
    def test_sort(self, path_or_module, function_name):
        """Test that get_functions_that_call returns all of the functions that
        call sort()
        """
        assert function_name in get_functions_that_call(path_or_module, {'sort'})

    @pytest.mark.parametrize('function_name', [
        name for name in EXAMPLES if 'sorted_' in name
    ])
    def test_sorted(self, path_or_module, function_name):
        """Test that get_functions_that_call returns all of the functions that
        call sort()
        """
        assert function_name in get_functions_that_call(path_or_module, {'sorted'})
