"""
Execution module for interfacing with Helm

:depends: pyhelm3
:platform: all

.. _pyhelm: https://github.com/azimuth-cloud/pyhelm3

:configuration: The following options can optionally be defined in the minion configuration. They will be passed through to the pyhelm3 client instantiation.

.. code-block:: yaml

    # Path to the Kubernetes client configuration.
    helm.kubeconfig: ...
    # Reference to the Kubernetes client configuration context.
    helm.kubecontext: ...
    # Path to the Helm executable.
    helm.executable: ...

.. note::
    This module use the "helm" command line. The "helm" binary has to be present in the PATH defined in the environment the Salt Minion is running under.
    Alternatively, a path to the binary can be defined in the minion configuration.
"""

import logging
from asyncio import run

log = logging.getLogger(__name__)

try:
    from pyhelm3 import Client
    from pyhelm3.errors import Error
    from pyhelm3.errors import ReleaseNotFoundError
    from pyhelm3.models import Release
    from pyhelm3.models import ReleaseRevision

    HAS_PYHELM = True
except ImportError:
    HAS_PYHELM = False


def __virtual__():
    if not HAS_PYHELM:
        return (
            False,
            "The helm execution module cannot be loaded: the pyhelm3 library is not available.",
        )

    # by default, pyhelm will print all commands it executes as INFO, which is very noisy in normal operation
    # pylint: disable=consider-using-in  # doesn't work here
    if logging.root.level != logging.DEBUG and log.level != logging.DEBUG:
        logging.getLogger("pyhelm3").setLevel(logging.WARN)

    return "helm"


def __init__(opts):
    if not HAS_PYHELM:
        return

    global c  # pylint: disable=global-statement # needed to share for command line use

    config = {}

    for option in [
        "kubeconfig",
        "kubecontext",
        "executable",
    ]:
        value = opts.get(f"helm.{option}")
        if value is not None:
            config[option] = value

    c = Client(**config)


# hack for tests as they don't invoke __init__ and __virtual__ like Salt does, is there a more proper way?
c = None  # pylint: disable=invalid-name
if c is None:
    __init__({})


async def _format_release(data, with_values=False):
    if isinstance(data, Release):
        release = data
        revision = await release.current_revision()

    elif isinstance(data, ReleaseRevision):
        revision = data
        release = revision.release

    else:
        raise ValueError("Unsupported invocation.")

    metadata = await revision.chart_metadata()

    out = {
        **release.model_dump(),
        "status": revision.status.value,
        "chart": {
            "name": metadata.name,
            "version": metadata.version,
        },
        "app_version": metadata.app_version,
        "revision": revision.revision,
    }

    if with_values:
        out["values"] = await revision.values()

    return out


async def _list_releases(**kwargs):
    out = []

    releases = await c.list_releases(**kwargs)

    for release in releases:
        out.append(await _format_release(release))

    return out


def list_releases(
    all=False,
    all_namespaces=False,
    include_deployed=True,
    include_failed=False,
    include_pending=False,
    include_superseded=False,
    include_uninstalled=False,
    include_uninstalling=False,
    max_releases=256,
    namespace=None,
    sort_by_date=False,
    sort_reversed=False,
):
    # pylint: disable=unused-argument
    """
    Query all installed releases.

    :param all:
    :param all_namespaces:
    :param include_deployed:
    :param include_failed:
    :param include_pending:
    :param include_superseded:
    :param include_uninstalled:
    :param include_uninstalling:
    :param max_releases:
    :param namespace:
    :param sort_by_date:
    :param sort_reversed:

    :return: List of release dicts.

    CLI Example:

    .. code-block:: bash

        salt '*' helm.list_releases all_namespaces=True
    """

    return run(_list_releases(**locals()))


async def _get_current_revision(release_name, namespace, with_values):
    out = {}

    try:
        return await _format_release(
            await c.get_current_revision(release_name, namespace=namespace), with_values
        )

    except ReleaseNotFoundError:
        return out


def get_current_revision(
    release_name,
    namespace=None,
    with_values=False,
):
    """
    Query a single installed release.

    :param release_name:
    :param namespace:
    :param with_values: Whether to include a dict of user values.

    :return: A dict with information about the installed the release, or an empty dict if nothing matched the given name.

    CLI Example:

    .. code-block:: bash

        salt '*' helm.get_current_revision cert-manager
    """

    return run(_get_current_revision(release_name, namespace, with_values))


async def _get_chart(name, version, as_obj):
    try:
        chart = await c.get_chart(name, version=version)

        # for use in the state module
        if as_obj:
            return chart

        # for use on the command line
        return chart.model_dump()

    except Error as err:
        return {"error": err}


def get_chart(name, version=None, as_obj=False):
    """
    Query a chart.

    :param name: Either an OCI URL or a repository/name reference.
    :param version: Optionally, a specific version to retrieve.
    :param as_obj: Whether to return the Chart() model instead of a dict. This will not work on the command line.

    :return: A dict with information about the chart, or a Chart object if as_obj is set to True.

    CLI Example:

    .. code-block:: bash

        salt '*' helm.get_chart oci://dp.apps.rancher.io/charts/cert-manager 1.19.1
    """

    return run(_get_chart(name, version, as_obj))


async def _install_or_upgrade_release(*args, **kwargs):
    try:
        return await c.install_or_upgrade_release(*args, **kwargs)

    except Error as err:
        return {"error": err}


def install_or_upgrade_release(
    release_name,
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
    # pylint: disable=unused-argument
    """
    Install or upgrade a release.

    :param release_name:
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

    :return: A ReleaseRevision object on success, or, in case of an exception, a dict containing an "error" key with the error message as the value.

    CLI Example:

    .. code-block:: bash

        salt '*' helm.install_or_upgrade_release my-cert-manager chart=oci://dp.apps.rancher.io/charts/cert-manager namespace=myspace
    """

    l = locals()
    release_name = l.pop("release_name")
    chart = l.pop("chart")
    values = l.pop("values")

    if isinstance(chart, str):
        chart = get_chart(chart, as_obj=True)

    return run(_install_or_upgrade_release(release_name, chart, values, **l))


async def _uninstall_release(**kwargs):
    return await c.uninstall_release(**kwargs)


def uninstall_release(
    release_name,
    dry_run=False,
    keep_history=False,
    namespace=None,
    no_hooks=False,
    timeout=None,
    wait=False,
):
    # pylint: disable=unused-argument
    """
    Uninstall a release.

    :param release_name:
    :param dry_run:
    :param keep_history:
    :param namespace:
    :param no_hooks:
    :param timeout:
    :param wait:

    :return: None

    CLI Example:

    .. code-block:: bash

        salt '*' helm.uninstall_release my-cert-manager namespace=myspace
    """

    return run(_uninstall_release(**locals()))
