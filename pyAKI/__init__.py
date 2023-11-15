from pyAKI.kdigo import Analyser

from pbr.version import VersionInfo  # type: ignore

# Check the PBR version module docs for other options than release_string()
__version__ = VersionInfo("pyAKI").release_string()
