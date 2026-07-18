import pyhelm3
import pytest
from salt.exceptions import CommandExecutionError

from saltext.helm.modules import helm


@pytest.fixture(scope="module", autouse=True)
def configure_loader_modules():
    return {helm: {}}


@pytest.fixture
def release():
    return {
        "name": "cert-manager",
        "app_version": "1.19.2",
        "namespace": "default",
        "revision": 5,
        "status": "deployed",
        "chart": {
            "name": "cert-manager",
            "version": "1.19.2",
        },
    }


def test_list_releases(fake_run, release):
    res = helm.list_releases()

    # only test first element here, we don't mock the individual status output of all releases in the mocked list output
    assert isinstance(res, list)
    assert res[0] == release


def test_get_current_revision(fake_run, release):
    res = helm.get_current_revision("cert-manager")

    assert isinstance(res, dict)
    assert res == release


def test_get_chart(fake_run):
    res = helm.get_chart("oci://dp.apps.rancher.io/charts/cert-manager")

    assert isinstance(res, dict)

    # only comparing a couple fields here, information is mostly passed through 1:1 from pyhelm
    assert res.get("ref") == "oci://dp.apps.rancher.io/charts/cert-manager"
    assert res.get("metadata", {}).get("app_version") == "1.19.2"

    res = helm.get_chart("oci://dp.apps.rancher.io/charts/cert-manager", "1.19.2")

    assert isinstance(res, dict)

    assert res.get("ref") == "oci://dp.apps.rancher.io/charts/cert-manager"
    assert res.get("metadata", {}).get("app_version") == "1.19.2"

    res = helm.get_chart("oci://dp.apps.rancher.io/charts/cert-manager", "1.19.2", as_obj=True)

    assert isinstance(res, pyhelm3.models.Chart)


def test_get_chart_error():
    with pytest.raises(CommandExecutionError):
        helm.get_chart("waddabunchononsense")


def test_install_or_upgrade_release(fake_run):
    res = helm.install_or_upgrade_release(
        "cert-manager",
        "oci://dp.apps.rancher.io/charts/cert-manager",
        {"crds": {"enable": False}},
    )

    assert isinstance(res, dict)
    assert res["status"] == "deployed"


def test_uninstall_release(fake_run):
    res = helm.uninstall_release(
        "cert-manager",
        namespace="default",
    )

    assert res is None
