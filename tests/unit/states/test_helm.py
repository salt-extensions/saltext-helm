# pylint: disable=use-implicit-booleaness-not-comparison  # asserting the return as it is written in the tested function is more readable

import datetime
from unittest.mock import MagicMock
from unittest.mock import patch

import pyhelm3  # pylint: disable=import-error  # works under nox
import pytest

from saltext.helm.states import helm

MOCK_CHART = pyhelm3.models.Chart(
    _command="nothing",
    ref="oci://dp.apps.rancher.io/charts/cert-manager",
    metadata={
        "name": "cert-manager",
        "version": "1.19.2",
        "apiVersion": "v2",
    },
    _values={
        "crds": {"enabled": False},
    },
)

MOCK_RELEASE = pyhelm3.models.Release(
    _command="nothing",
    name="cert-manager",
    namespace="test",
)


@pytest.fixture
def configure_loader_modules():
    return {helm: {}}


@pytest.mark.parametrize("test", [True, False])
def test_release_present_new(test):
    mock_release_revision_in = {}

    mock_release_revision_out = pyhelm3.models.ReleaseRevision(
        _command="nothing",
        app_version="1.19.2",
        chart=MOCK_CHART,
        name="cert-manager",
        namespace="testspace",
        revision=7,
        status=pyhelm3.models.ReleaseRevisionStatus.DEPLOYED,
        values={
            "crds": {"enabled": False},
        },
        release=MOCK_RELEASE,
        updated=datetime.MINYEAR,
    )

    with (
        patch.dict(helm.__opts__, {"test": test}),
        patch.dict(
            helm.__salt__,
            {
                "helm.get_chart": MagicMock(return_value=MOCK_CHART),
                "helm.get_current_revision": MagicMock(return_value=mock_release_revision_in),
                "helm.install_or_upgrade_release": MagicMock(
                    return_value=mock_release_revision_out,
                ),
            },
        ),
    ):
        res = helm.release_present(
            name="cert-manager",
            chart={
                "name": "oci://dp.apps.rancher.io/charts/cert-manager",
                "version": "1.19.2",
            },
            values={"crds": {"enabled": False}},
            description="Hello World!",
            namespace="test",
        )

        assert res["name"] == "cert-manager"

        if test:
            assert res["result"] is None
            assert res["changes"] == {
                "old": None,
                "new": {
                    "chart": {
                        "name": "cert-manager",
                        "version": "1.19.2",
                    },
                    "values": {"crds": {"enabled": False}},
                },
            }
            assert res["comment"] == "Would install release."

        else:
            assert res["result"] is True
            assert res["changes"] == {
                "old": None,
                "new": {
                    "status": "deployed",
                    "name": "cert-manager",
                    "namespace": "test",
                    "chart": {"name": "cert-manager", "version": "1.19.2"},
                    "values": {"crds": {"enabled": False}},
                },
            }
            assert res["comment"] == "Successfully installed release."


@pytest.mark.parametrize("test", [True, False])
def test_release_present_changed_values(test):
    mock_release_revision_in = {
        "app_version": "1.19.2",
        "chart": {
            "name": "cert-manager",
            "version": "1.19.2",
        },
        "name": "cert-manager",
        "namespace": "testspace",
        "revision": 7,
        "status": "deployed",
        "values": {
            "crds": {"enabled": True},
        },
    }

    mock_release_revision_out = pyhelm3.models.ReleaseRevision(
        _command="nothing",
        app_version="1.19.2",
        chart=MOCK_CHART,
        name="cert-manager",
        namespace="testspace",
        revision=7,
        status=pyhelm3.models.ReleaseRevisionStatus.DEPLOYED,
        values={
            "crds": {"enabled": False},
        },
        release=MOCK_RELEASE,
        updated=datetime.MINYEAR,
    )

    with (
        patch.dict(helm.__opts__, {"test": test}),
        patch.dict(
            helm.__salt__,
            {
                "helm.get_chart": MagicMock(return_value=MOCK_CHART),
                "helm.get_current_revision": MagicMock(return_value=mock_release_revision_in),
                "helm.install_or_upgrade_release": MagicMock(
                    return_value=mock_release_revision_out,
                ),
            },
        ),
    ):
        res = helm.release_present(
            name="cert-manager",
            chart={
                "name": "oci://dp.apps.rancher.io/charts/cert-manager",
                "version": "1.19.2",
            },
            values={"crds": {"enabled": False}},
            description="Hello World!",
            namespace="test",
        )

        assert res["name"] == "cert-manager"

        if test:
            assert res["result"] is None
            assert res["changes"] == {
                "old": {"values": {"crds": {"enabled": True}}},
                "new": {"values": {"crds": {"enabled": False}}},
            }
            assert res["comment"] == "Would update release."

        else:
            assert res["result"] is True
            assert res["changes"] == {
                "old": {"values": {"crds": {"enabled": True}}},
                "new": {
                    "status": "deployed",
                    "name": "cert-manager",
                    "namespace": "test",
                    "chart": {"name": "cert-manager", "version": "1.19.2"},
                    "values": {"crds": {"enabled": False}},
                },
            }
            assert res["comment"] == "Successfully updated release."


@pytest.mark.parametrize("test", [True, False])
def test_release_present_no_changes(test):
    mock_release_revision_in = {
        "app_version": "1.19.2",
        "chart": {
            "name": "cert-manager",
            "version": "1.19.2",
        },
        "name": "cert-manager",
        "namespace": "testspace",
        "revision": 7,
        "status": "deployed",
        "values": {
            "crds": {"enabled": True},
        },
    }

    with (
        patch.dict(helm.__opts__, {"test": test}),
        patch.dict(
            helm.__salt__,
            {
                "helm.get_chart": MagicMock(return_value=MOCK_CHART),
                "helm.get_current_revision": MagicMock(return_value=mock_release_revision_in),
            },
        ),
    ):
        res = helm.release_present(
            name="cert-manager",
            chart={
                "name": "oci://dp.apps.rancher.io/charts/cert-manager",
                "version": "1.19.2",
            },
            values={"crds": {"enabled": True}},
            description="Hello World!",
            namespace="test",
        )

        assert res["name"] == "cert-manager"

        assert res["result"] is True
        assert res["changes"] == {}
        assert res["comment"] == "Release matches the configuration."


@pytest.mark.parametrize("test", [True, False])
def test_release_absent(test):
    mock_release_revision_in = {
        "app_version": "1.19.2",
        "chart": {
            "name": "cert-manager",
            "version": "1.19.2",
        },
        "name": "cert-manager",
        "namespace": "testspace",
        "revision": 7,
        "status": "deployed",
        "values": {
            "crds": {"enabled": True},
        },
    }

    with (
        patch.dict(helm.__opts__, {"test": test}),
        patch.dict(
            helm.__salt__,
            {
                "helm.get_current_revision": MagicMock(side_effect=[mock_release_revision_in, {}]),
                "helm.uninstall_release": MagicMock(return_value=None),
            },
        ),
    ):
        res = helm.release_absent(
            name="cert-manager",
            namespace="testspace",
        )

        assert res["name"] == "cert-manager"
        assert res["changes"] == {
            "old": {
                "name": "cert-manager",
            },
            "new": {
                "name": None,
            },
        }

        if test:
            assert res["result"] is None
            assert res["comment"] == "Would uninstall release."

        else:
            assert res["result"] is True
            assert res["comment"] == "Successfully uninstalled release."
