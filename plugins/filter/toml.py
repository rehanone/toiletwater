# (c) 2017, Matt Martz <matt@sivel.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Works with: toml (>=0.10), tomli (>=2.0), tomli-w (>=1.0)
# Fallback order: toml → tomli + tomli-w

from __future__ import (absolute_import, division, print_function)

from ansible.errors import AnsibleFilterError
from ansible.module_utils._text import to_text
from ansible.module_utils.common._collections_compat import Mapping

# --------------------------------------------------------------------
# Helper: lazy-load TOML libraries with proper fallbacks
# --------------------------------------------------------------------
_toml_loader = None
_toml_dumper = None


def _import_toml():
    global _toml_loader, _toml_dumper
    if _toml_loader is not None:  # already resolved
        return

    try:
        import toml  # full-featured, supports both load & dump
        _toml_loader = toml.loads
        _toml_dumper = toml.dumps
        return
    except ImportError:
        pass

    # Fallback 1: tomli (read-only) + tomli-w (write-only)
    try:
        import tomli
        import tomli_w
        _toml_loader = tomli.loads
        _toml_dumper = tomli_w.dumps
        return
    except ImportError:
        pass

    # If we get here, nothing worked
    raise AnsibleFilterError(
        "The 'toml' or ('tomli' + 'tomli-w') Python package is required for to_toml/from_toml filters. "
        "Install with: pip install toml   # or   pip install tomli tomli-w"
    )


# --------------------------------------------------------------------
# Filter: from_toml
# --------------------------------------------------------------------
def from_toml(value):
    if not isinstance(value, (str, bytes)):
        raise AnsibleFilterError(f"from_toml expects a string, got {type(value).__name__}")

    _import_toml()
    text = to_text(value, errors="surrogate_or_strict")

    try:
        return _toml_loader(text)
    except Exception as e:
        raise AnsibleFilterError(f"Failed to parse TOML: {e}")


# --------------------------------------------------------------------
# Filter: to_toml
# --------------------------------------------------------------------
def to_toml(value):
    if not isinstance(value, Mapping):
        raise AnsibleFilterError(f"to_toml expects a dict-like object, got {type(value).__name__}")

    _import_toml()

    try:
        toml_string = _toml_dumper(value)
        return to_text(toml_string, errors="surrogate_or_strict")
    except Exception as e:
        raise AnsibleFilterError(f"Failed to serialize to TOML: {e}")


# --------------------------------------------------------------------
# Ansible FilterModule entry point
# --------------------------------------------------------------------
class FilterModule(object):
    def filters(self):
        return {
            'to_toml': to_toml,
            'from_toml': from_toml,
        }
