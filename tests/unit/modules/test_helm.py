from unittest.mock import patch

import pyhelm3  # pylint: disable=import-error  # works under nox
import pytest

from saltext.helm.modules import helm

RELEASE = {
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


def test_list_releases(fake_output):
    def side(command):
        if command[0] == "get":
            return fake_output.get(command[0] + "_" + command[1])

        return fake_output.get(command[0])

    with patch.object(pyhelm3.command.Command, "run", side_effect=side):
        res = helm.list_releases()

        # only test first element here, we don't mock the individual status output of all releases in the mocked list output
        assert isinstance(res, list)
        assert res[0] == RELEASE


def test_get_current_revision(fake_output):
    def side(command):
        if command[0] == "get":
            return fake_output.get(command[0] + "_" + command[1])

        return fake_output.get(command[0])

    with patch.object(pyhelm3.command.Command, "run", side_effect=side):
        res = helm.get_current_revision("cert-manager")

        assert isinstance(res, dict)
        assert res == RELEASE


def test_get_chart(fake_output):
    def side(command):
        return fake_output.get(command[0] + "_" + command[1])

    with patch.object(pyhelm3.command.Command, "run", side_effect=side):
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


def test_install_or_upgrade_release(fake_output):
    def side(
        command, stdin=None
    ):  # pylint: disable=unused-argument  # patch passes the second argumenteven if we do not use it
        # if needed to make the mocking more dynamic in the future, values upon "upgrade" get passed as stdin here

        if command[0] == "upgrade":
            return fake_output.get(command[0])
        if command[0] == "show" or command[0] == "get":
            return fake_output.get(command[0] + "_" + command[1])

        pytest.fail("Incomplete side effect.")

    with patch.object(pyhelm3.command.Command, "run", side_effect=side):
        res = helm.install_or_upgrade_release(
            "cert-manager",
            "oci://dp.apps.rancher.io/charts/cert-manager",
            {"crds": {"enable": False}},
        )

        assert isinstance(res, pyhelm3.models.ReleaseRevision)
        assert res.status.value == "deployed"


def test_uninstall_release(fake_output):
    def side(command):
        if command[0] == "show" or command[0] == "get":
            return fake_output.get(command[0] + "_" + command[1])

    with patch.object(pyhelm3.command.Command, "run", side_effect=side):
        res = helm.uninstall_release(
            "cert-manager",
            namespace="default",
        )

        assert res is None
