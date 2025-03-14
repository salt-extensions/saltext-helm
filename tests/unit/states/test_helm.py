"""
Test cases for salt.modules.helm
"""

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from saltext.helm.states import helm


@pytest.fixture
def configure_loader_modules():
    return {helm: {}}


def test_repo_managed_import_failed_repo_manage():
    ret = {
        "name": "state_id",
        "changes": {},
        "result": False,
        "comment": "'helm.repo_manage' modules not available on this minion.",
    }
    assert helm.repo_managed("state_id") == ret


def test_repo_managed_import_failed_repo_update():
    mock_helm_modules = {"helm.repo_manage": MagicMock(return_value=True)}
    with patch.dict(helm.__salt__, mock_helm_modules):
        ret = {
            "name": "state_id",
            "changes": {},
            "result": False,
            "comment": "'helm.repo_update' modules not available on this minion.",
        }
        assert helm.repo_managed("state_id") == ret


def test_repo_managed_is_testing():
    mock_helm_modules = {
        "helm.repo_manage": MagicMock(return_value=True),
        "helm.repo_update": MagicMock(return_value=True),
    }
    with patch.dict(helm.__salt__, mock_helm_modules):
        mock__opts__ = {"test": MagicMock(return_value=True)}
        with patch.dict(helm.__opts__, mock__opts__):
            ret = {
                "name": "state_id",
                "result": None,
                "comment": "Helm repo would have been managed.",
                "changes": {},
            }
            assert helm.repo_managed("state_id") == ret


def test_repo_managed_success():
    result_changes = {"added": True, "removed": True, "failed": False}
    mock_helm_modules = {
        "helm.repo_manage": MagicMock(return_value=result_changes),
        "helm.repo_update": MagicMock(return_value=True),
    }
    with patch.dict(helm.__salt__, mock_helm_modules):
        ret = {
            "name": "state_id",
            "result": True,
            "comment": "Repositories were added or removed.",
            "changes": result_changes,
        }
        assert helm.repo_managed("state_id") == ret


def test_repo_managed_success_with_update():
    result_changes = {"added": True, "removed": True, "failed": False}
    mock_helm_modules = {
        "helm.repo_manage": MagicMock(return_value=result_changes),
        "helm.repo_update": MagicMock(return_value=True),
    }
    result_wanted = result_changes
    result_wanted.update({"repo_update": True})
    with patch.dict(helm.__salt__, mock_helm_modules):
        ret = {
            "name": "state_id",
            "result": True,
            "comment": "Repositories were added or removed.",
            "changes": result_wanted,
        }
        assert helm.repo_managed("state_id") == ret


def test_repo_managed_failed():
    result_changes = {"added": True, "removed": True, "failed": True}
    mock_helm_modules = {
        "helm.repo_manage": MagicMock(return_value=result_changes),
        "helm.repo_update": MagicMock(return_value=True),
    }
    with patch.dict(helm.__salt__, mock_helm_modules):
        ret = {
            "name": "state_id",
            "result": False,
            "comment": "Failed to add or remove some repositories.",
            "changes": result_changes,
        }
        assert helm.repo_managed("state_id") == ret


def test_repo_updated_import_failed():
    ret = {
        "name": "state_id",
        "changes": {},
        "result": False,
        "comment": "'helm.repo_update' modules not available on this minion.",
    }
    assert helm.repo_updated("state_id") == ret


def test_repo_updated_is_testing():
    mock_helm_modules = {"helm.repo_update": MagicMock(return_value=True)}
    with patch.dict(helm.__salt__, mock_helm_modules):
        mock__opts__ = {"test": MagicMock(return_value=True)}
        with patch.dict(helm.__opts__, mock__opts__):
            ret = {
                "name": "state_id",
                "result": None,
                "comment": "Helm repo would have been updated.",
                "changes": {},
            }
            assert helm.repo_updated("state_id") == ret


def test_repo_updated_success():
    mock_helm_modules = {"helm.repo_update": MagicMock(return_value=True)}
    with patch.dict(helm.__salt__, mock_helm_modules):
        ret = {
            "name": "state_id",
            "result": True,
            "comment": "Helm repo is updated.",
            "changes": {},
        }
        assert helm.repo_updated("state_id") == ret


def test_repo_updated_failed():
    mock_helm_modules = {"helm.repo_update": MagicMock(return_value=False)}
    with patch.dict(helm.__salt__, mock_helm_modules):
        ret = {
            "name": "state_id",
            "result": False,
            "comment": "Failed to sync some repositories.",
            "changes": False,
        }
        assert helm.repo_updated("state_id") == ret


def test_release_present_import_failed_helm_status():
    ret = {
        "name": "state_id",
        "changes": {},
        "result": False,
        "comment": "'helm.status' modules not available on this minion.",
    }
    assert helm.release_present("state_id", "mychart") == ret


def test_release_present_import_failed_helm_install():
    mock_helm_modules = {"helm.status": MagicMock(return_value=True)}
    with patch.dict(helm.__salt__, mock_helm_modules):
        ret = {
            "name": "state_id",
            "changes": {},
            "result": False,
            "comment": "'helm.install' modules not available on this minion.",
        }
        assert helm.release_present("state_id", "mychart") == ret


def test_release_present_import_failed_helm_upgrade():
    mock_helm_modules = {
        "helm.status": MagicMock(return_value=True),
        "helm.install": MagicMock(return_value=True),
    }
    with patch.dict(helm.__salt__, mock_helm_modules):
        ret = {
            "name": "state_id",
            "changes": {},
            "result": False,
            "comment": "'helm.upgrade' modules not available on this minion.",
        }
        assert helm.release_present("state_id", "mychart") == ret


def test_release_present_is_testing():
    mock_helm_modules = {
        "helm.status": MagicMock(return_value=True),
        "helm.install": MagicMock(return_value=True),
        "helm.upgrade": MagicMock(return_value=True),
    }
    with patch.dict(helm.__salt__, mock_helm_modules):
        mock__opts__ = {"test": MagicMock(return_value=True)}
        with patch.dict(helm.__opts__, mock__opts__):
            ret = {
                "name": "state_id",
                "result": None,
                "comment": "Helm release would have been installed or updated.",
                "changes": {},
            }
            assert helm.release_present("state_id", "mychart") == ret


def test_release_absent_import_failed_helm_uninstall():
    ret = {
        "name": "state_id",
        "changes": {},
        "result": False,
        "comment": "'helm.uninstall' modules not available on this minion.",
    }
    assert helm.release_absent("state_id") == ret


def test_release_absent_import_failed_helm_status():
    mock_helm_modules = {"helm.uninstall": MagicMock(return_value=True)}
    with patch.dict(helm.__salt__, mock_helm_modules):
        ret = {
            "name": "state_id",
            "changes": {},
            "result": False,
            "comment": "'helm.status' modules not available on this minion.",
        }
        assert helm.release_absent("state_id") == ret


def test_release_absent_is_testing():
    mock_helm_modules = {
        "helm.status": MagicMock(return_value=True),
        "helm.uninstall": MagicMock(return_value=True),
    }
    with patch.dict(helm.__salt__, mock_helm_modules):
        mock__opts__ = {"test": MagicMock(return_value=True)}
        with patch.dict(helm.__opts__, mock__opts__):
            ret = {
                "name": "state_id",
                "result": None,
                "comment": "Helm release would have been uninstalled.",
                "changes": {},
            }
            assert helm.release_absent("state_id") == ret


def test_release_absent_success():
    mock_helm_modules = {
        "helm.status": MagicMock(return_value={}),
        "helm.uninstall": MagicMock(return_value=True),
    }
    with patch.dict(helm.__salt__, mock_helm_modules):
        ret = {
            "name": "state_id",
            "result": True,
            "comment": "Helm release state_id is absent.",
            "changes": {"absent": "state_id"},
        }
        assert helm.release_absent("state_id") == ret


def test_release_absent_error():
    mock_helm_modules = {
        "helm.status": MagicMock(return_value={}),
        "helm.uninstall": MagicMock(return_value="error"),
    }
    with patch.dict(helm.__salt__, mock_helm_modules):
        ret = {
            "name": "state_id",
            "result": False,
            "comment": "error",
            "changes": {},
        }
        assert helm.release_absent("state_id") == ret
