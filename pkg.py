"""
pkg.py: Build vpp-detect's macOS packages
"""

import os
import argparse
import subprocess
import macos_pkg_builder
import mac_signing_buddy

from pathlib import Path


SOURCE_VERSION_PATH: str = "vpp-detect.m"
SCRIPTS_PATH:        str = "Packaging/Scripts"


class Build:

    def __init__(self,
                 app_signing_identity: str = None,
                 pkg_signing_identity: str = None,
                 notarize_apple_id: str = None,
                 notarize_password: str = None,
                 notarize_team_id: str = None
        ) -> None:

        self.app_signing_identity = app_signing_identity
        self.pkg_signing_identity = pkg_signing_identity
        self.notarize_apple_id = notarize_apple_id
        self.notarize_password = notarize_password
        self.notarize_team_id = notarize_team_id

        self.can_sign_app = self.app_signing_identity is not None
        self.can_notarize = all([self.notarize_apple_id, self.notarize_password, self.notarize_team_id])

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
            pkg_signing_identity=self.pkg_signing_identity,
        ).build() is True

        if self.can_notarize:
            print("Notarizing Uninstall-VPP-Detect.pkg...")
            mac_signing_buddy.Notarize(
                file="Packaging/Uninstall-VPP-Detect.pkg",
                apple_id=self.notarize_apple_id,
                password=self.notarize_password,
                team_id=self.notarize_team_id,
            ).sign()


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

        if self.can_sign_app:
            print("Signing vpp-detect...")
            mac_signing_buddy.Sign(
                file="vpp-detect",
                identity=self.app_signing_identity,
            ).sign()

        if self.can_notarize:
            print("Notarizing vpp-detect...")
            mac_signing_buddy.Notarize(
                file="vpp-detect",
                apple_id=self.notarize_apple_id,
                password=self.notarize_password,
                team_id=self.notarize_team_id,
            ).sign()

        assert macos_pkg_builder.Packages(
            pkg_output="Packaging/Install-VPP-Detect.pkg",
            pkg_bundle_id="com.ripeda.vpp-detect",
            pkg_version=self.version,
            pkg_file_structure={
                "vpp-detect": "/usr/local/bin/vpp-detect"
            },
            pkg_preinstall_script=Path(SCRIPTS_PATH, "preinstall"),
            pkg_postinstall_script=Path(SCRIPTS_PATH, "postinstall"),
            pkg_signing_identity=self.pkg_signing_identity,
        ).build() is True

        if self.can_notarize:
            print("Notarizing Install-VPP-Detect.pkg...")
            mac_signing_buddy.Notarize(
                file="Packaging/Install-VPP-Detect.pkg",
                apple_id=self.notarize_apple_id,
                password=self.notarize_password,
                team_id=self.notarize_team_id,
            ).sign()


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    parser = argparse.ArgumentParser(description="Build VPP-Detect.")
    parser.add_argument("--app_signing_identity", type=str, help="App Signing identity")
    parser.add_argument("--pkg_signing_identity", type=str, help="PKG Signing identity")
    parser.add_argument("--notarize_apple_id", type=str, help="Apple ID")
    parser.add_argument("--notarize_password", type=str, help="Password")
    parser.add_argument("--notarize_team_id", type=str, help="Team ID")

    args = parser.parse_args()

    Build(
        app_signing_identity=args.app_signing_identity,
        pkg_signing_identity=args.pkg_signing_identity,
        notarize_apple_id=args.notarize_apple_id,
        notarize_password=args.notarize_password,
        notarize_team_id=args.notarize_team_id,
    )

    print("Done")
