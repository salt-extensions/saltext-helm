"""
State module for interfacing with Helm

.. note::
    Reference the configuration notes in the documentation of the Helm execution module.
"""

import logging

from salt.exceptions import CommandExecutionError

log = logging.getLogger(__name__)


def __virtual__():
    # just testing for any one of the functions here
    if "helm.get_chart" in __salt__:
        return "helm"

    return (False, "The helm state module cannot be loaded: the pyhelm3 library is not available.")


def _changes(ret):
    if "old" not in ret["changes"]:
        ret["changes"] = {"old": {}, "new": {}}


def _chart(name, version):
    # convenience function, return:
    # - a chart dict comparable to the input values
    # - a chart reference usable for install/upgrade
    # unfortunately there appears to be no way to get the registry URL a release was originally installed with, so in case of charts from OCI registries, we can only compare name and version

    out = {"name": None, "version": None}

    chart = __salt__["helm.get_chart"](name, version, as_obj=True)

    metadata = chart.metadata
    out["name"] = metadata.name
    out["version"] = metadata.version

    return out, chart


def release_present(
    name,
    chart,
    values=None,
    atomic=False,
    cleanup_on_fail=False,
    create_namespace=True,
    description=None,
    dry_run=False,
    force=False,
    namespace=None,
    no_hooks=False,
    reset_values=False,
    reuse_values=False,
    skip_crds=False,
    timeout=None,
    wait=False,
    disable_validation=False,
):
    """
    Ensure a release is installed and configured with the given chart and values.

    :param name:
    :param chart: Either a Chart object, a OCI URL, or a repository/name reference.
    :param values: Dict of user values.
    :param atomic:
    :param cleanup_on_fail:
    :param create_namespace:
    :param description:
    :param dry_run:
    :param force:
    :param namespace:
    :param no_hooks:
    :param reset_values:
    :param reuse_values:
    :param skip_crds:
    :param timeout:
    :param wait:
    :param disable_validation:
    """

    if "name" not in chart or "version" not in chart:
        raise ValueError('Both "name" and "version" are required in the "chart" dict.')

    ret = {"name": name, "changes": {}, "comment": "", "result": None}

    try:
        have_revision = __salt__["helm.get_current_revision"](name, namespace, with_values=True)
    except CommandExecutionError as err:
        ret["comment"] = f"Failed to retrieve current revision.\n{err}"
        ret["result"] = False

        return ret

    try:
        want_chart, want_chart_obj = _chart(**chart)
    except CommandExecutionError as err:
        ret["comment"] = f"Failed to retrieve chart metadata for {chart}.\n{err}."
        ret["result"] = False

        return ret

    want_values = values or {}

    if have_revision:
        have_chart = have_revision["chart"]
        have_values = have_revision["values"]

        if have_chart != want_chart:
            _changes(ret)

            ret["changes"]["old"]["chart"] = have_chart
            ret["changes"]["new"]["chart"] = want_chart

        if have_values != want_values:
            _changes(ret)

            ret["changes"]["old"]["values"] = have_values
            ret["changes"]["new"]["values"] = want_values

        if not ret["changes"]:
            ret["comment"] = "Release matches the configuration."
            ret["result"] = True

            return ret

        if __opts__["test"]:
            ret["comment"] = "Would update release."

            return ret

    if __opts__["test"]:
        _changes(ret)

        ret["changes"] = {
            "old": None,
            "new": {
                "chart": want_chart,
                "values": want_values,
            },
        }
        ret["comment"] = "Would install release."

        return ret

    try:
        new_release = __salt__["helm.install_or_upgrade_release"](
            name,
            want_chart_obj,
            want_values,
            atomic,
            cleanup_on_fail=cleanup_on_fail,
            create_namespace=create_namespace,
            description=description,
            dry_run=dry_run,
            force=force,
            namespace=namespace,
            no_hooks=no_hooks,
            reset_values=reset_values,
            reuse_values=reuse_values,
            skip_crds=skip_crds,
            timeout=timeout,
            wait=wait,
            disable_validation=disable_validation,
        )

    except CommandExecutionError as err:
        ret["comment"] = f"Failed to install or upgrade release.\n{err}."
        ret["result"] = False

        return ret

    ret["result"] = True
    rel = dict(new_release.get("release", {}))
    ret["changes"]["new"] = {
        "status": new_release.get("status"),
        "name": rel.get("name"),
        "namespace": rel.get("namespace"),
        # cleaner might be to retrieve chart_metadata from new_result, but it would require another async call - for now let's assume that helm actually installed name+version as given
        "chart": want_chart,
        "values": want_values,
    }

    if "old" in ret["changes"]:
        ret["comment"] = "Successfully updated release."

    else:
        ret["changes"]["old"] = None
        ret["comment"] = "Successfully installed release."

    return ret


def release_absent(
    name,
    dry_run=False,
    namespace=None,
    keep_history=False,
    no_hooks=False,
    timeout=None,
    wait=False,
):
    """
    Ensure a release is not installed.

    :param name:
    :param dry_run:
    :param namespace:
    :param keep_history:
    :param no_hooks:
    :param timeout:
    :param wait:
    """

    ret = {"name": name, "changes": {}, "comment": "", "result": None}

    try:
        have_revision = __salt__["helm.get_current_revision"](name, namespace)
    except CommandExecutionError as err:
        ret["comment"] = f"Failed to retrieve current revision.\n{err}"
        ret["result"] = False

        return ret

    if not have_revision:
        ret["comment"] = "Release is already absent."
        ret["result"] = True

        return ret

    ret["changes"] = {
        "old": {
            "name": name,
        },
        "new": {
            "name": None,
        },
    }

    if __opts__["test"]:
        ret["comment"] = "Would uninstall release."

        return ret

    try:
        __salt__["helm.uninstall_release"](
            name,
            dry_run,
            keep_history,
            namespace,
            no_hooks,
            timeout,
            wait,
        )

    except CommandExecutionError as err:
        ret["comment"] = f"Failed to uninstall release.\n{err}."
        ret["result"] = False
        ret["changes"] = {}

    have_revision_after = __salt__["helm.get_current_revision"](name, namespace)

    if have_revision_after:
        ret["comment"] = "Release still present after uninstall."
        ret["result"] = False
        ret["changes"] = {}

        return ret

    ret["comment"] = "Successfully uninstalled release."
    ret["result"] = True

    return ret
