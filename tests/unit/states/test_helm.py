import pytest
import salt.modules.test as testmod
import saltext.helm.modules.helm_mod as helm_module
import saltext.helm.states.helm_mod as helm_state


@pytest.fixture
def configure_loader_modules():
    return {
        helm_module: {
            "__salt__": {
                "test.echo": testmod.echo,
            },
        },
        helm_state: {
            "__salt__": {
                "helm.example_function": helm_module.example_function,
            },
        },
    }


def test_replace_this_this_with_something_meaningful():
    echo_str = "Echoed!"
    expected = {
        "name": echo_str,
        "changes": {},
        "result": True,
        "comment": f"The 'helm.example_function' returned: '{echo_str}'",
    }
    assert helm_state.exampled(echo_str) == expected
