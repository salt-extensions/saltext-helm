# Installation

Generally, extensions need to be installed into the same Python environment Salt uses.

:::{tab} State
```yaml
Install Salt Helm extension:
  pip.installed:
    - names:
        - saltext-helm
        - git+https://github.com/azimuth-cloud/pyhelm3.git
```
:::

:::{tab} Onedir installation
```bash
salt-pip install saltext-helm
```
:::

:::{tab} Regular installation
```bash
pip install saltext-helm
```
:::

:::{hint}
Saltexts are not distributed automatically via the fileserver like custom modules, they need to be installed
on each node you want them to be available on.
:::
