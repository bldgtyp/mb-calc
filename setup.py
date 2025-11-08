"""Build configuration for packaging MB Calc as a macOS app with py2app."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from setuptools import find_packages, setup  # type: ignore[import-not-found]

try:  # py2app is only needed for building the bundle
    from py2app.build_app import py2app as py2app_build_command  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover - build-time dependency handled in dev extras
    py2app_build_command = None  # type: ignore[assignment]

BASE_DIR = Path(__file__).parent
RESOURCES_DIR = BASE_DIR / "src" / "mb_calc"

APP = ["scripts/mb_calc_app.py"]
DATA_FILES: list[str] = []
OPTIONS = {
    "argv_emulation": False,
    "packages": ["mb_calc"],
    "excludes": ["tkinter", "Tcl", "Tk"],
    "plist": {
        "CFBundleName": "MB Calc",
        "CFBundleIdentifier": "com.bldgtyp.mbcalc",
        "LSUIElement": True,  # hide Dock icon since we are a menu-bar app
    },
}

icon_resource = RESOURCES_DIR / "calculator-icon-original.svg"
if icon_resource.exists():
    OPTIONS.setdefault("resources", []).append(str(icon_resource))

entitlements_file = BASE_DIR / "entitlements.plist"
code_sign_identity = os.environ.get("MB_CALC_CODESIGN_IDENTITY")


def _codesign(app_path: Path, identity: str) -> None:
    """Run codesign over the built app bundle."""

    command = [
        "codesign",
        "--deep",
        "--force",
        "--options",
        "runtime",
        "--timestamp",
        "--sign",
        identity,
        str(app_path),
    ]
    if entitlements_file.exists():
        command.extend(["--entitlements", str(entitlements_file)])
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:  # pragma: no cover - best effort messaging
        stderr = exc.stderr or ""
        if "ambiguous" in stderr:
            msg = (
                "codesign identity is ambiguous; set MB_CALC_CODESIGN_IDENTITY to the SHA-1 fingerprint, "
                "e.g. output from `security find-identity -p codesigning -v`."
            )
            raise SystemExit(msg) from exc
        raise


def _maybe_codesign_app(dist_dir: Path) -> None:
    app_path = dist_dir / "MB Calc.app"
    if not app_path.exists():
        return
    if not code_sign_identity:
        print("MB_CALC_CODESIGN_IDENTITY not set; skipping codesign step.")
        return
    _codesign(app_path, code_sign_identity)


cmdclass = {}
if py2app_build_command is not None:

    class SignedPy2App(py2app_build_command):  # type: ignore[misc]
        """py2app command wrapper that codesigns after packaging."""

        def run(self):  # type: ignore[override]
            super().run()
            _maybe_codesign_app(Path(self.dist_dir))

    cmdclass["py2app"] = SignedPy2App

setup(
    app=APP,
    name="MB Calc",
    options={"py2app": OPTIONS},
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={"mb_calc": ["calculator-icon-original.svg"]},
    cmdclass=cmdclass,
)
