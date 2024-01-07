import pytest

pytestmark = [
    pytest.mark.requires_salt_states("helm.exampled"),
]


@pytest.fixture
def helm(states):
    return states.helm


def test_replace_this_this_with_something_meaningful(helm):
    echo_str = "Echoed!"
    ret = helm.exampled(echo_str)
    assert ret.result
    assert not ret.changes
    assert echo_str in ret.comment
