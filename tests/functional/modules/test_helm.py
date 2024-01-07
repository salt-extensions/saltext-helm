import pytest

pytestmark = [
    pytest.mark.requires_salt_modules("helm.example_function"),
]


@pytest.fixture
def helm(modules):
    return modules.helm


def test_replace_this_this_with_something_meaningful(helm):
    echo_str = "Echoed!"
    res = helm.example_function(echo_str)
    assert res == echo_str
