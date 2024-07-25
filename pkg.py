"""
pkg.py: Build vpp-detect's macOS packages
"""

import os
import subprocess
import macos_pkg_builder

from pathlib import Path


SOURCE_VERSION_PATH: str = "vpp-detect.m"
SCRIPTS_PATH:        str = "Packaging/Scripts"


class Build:

    def __init__(self) -> None:
        self.version = "0.0.0"

        self._fetch_app_version()
        self._build_uninstall_pkg()
        self._build_install_pkg()


    def _fetch_app_version(self) -> None:
        """
        Load source file, find version number, and set self.version
        """
        if not Path(SOURCE_VERSION_PATH).is_file():
            raise Exception("Source file not found")

        with open(SOURCE_VERSION_PATH, "r") as f:
            for line in f.readlines():
                if line.startswith("#define VERSION "):
                    self.version = line.split()[2][1:-1]
                    return


    def _build_uninstall_pkg(self) -> None:
        print("Building uninstall pkg...")
        assert macos_pkg_builder.Packages(
            pkg_output="Packaging/Uninstall-VPP-Detect.pkg",
            pkg_bundle_id="com.ripeda.vpp-detect-uninstaller",
            pkg_version=self.version,
            pkg_preinstall_script=Path(SCRIPTS_PATH, "preinstall"),
        ).build() is True


    def _build_install_pkg(self) -> None:
        print("Building install pkg...")

        if Path("vpp-detect").is_file():
            Path("vpp-detect").unlink()

        result = subprocess.run([
            "/usr/bin/clang",
             "-framework", "Foundation",
             "-arch", "x86_64",
             "-arch", "arm64",
             "-o", "vpp-detect", "vpp-detect.m",
        ], capture_output=True)
        if result.returncode != 0:
            print("Failed to compile vpp-detect")
            print(result.stdout)
            print(result.stderr)
            exit(1)

        assert macos_pkg_builder.Packages(
            pkg_output="Packaging/Install-VPP-Detect.pkg",
            pkg_bundle_id="com.ripeda.vpp-detect",
            pkg_version=self.version,
            pkg_file_structure={
                "vpp-detect": "/usr/local/bin/vpp-detect"
            },
            pkg_preinstall_script=Path(SCRIPTS_PATH, "preinstall"),
            pkg_postinstall_script=Path(SCRIPTS_PATH, "postinstall"),
        ).build() is True


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    Build()
    print("Done")
