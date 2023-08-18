import os
import subprocess
from pathlib import Path


SOURCE_VERSION_PATH:   str = "vpp-detect.m"
INSTALL_SCRIPT_PATH:   str = "Packaging/Install Scripts"
UNINSTALL_SCRIPT_PATH: str = "Packaging/Uninstall Scripts"


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

    def _remove_old_pkgs(self) -> None:
        """
        Remove old pkg files
        """
        for file in Path("./Packaging").iterdir():
            if file.suffix == ".pkg":
                print(f"Removing old pkg: {file.name}")
                file.unlink()

    def _build_uninstall_pkg(self) -> None:
        print("Building uninstall pkg...")
        for file in Path(UNINSTALL_SCRIPT_PATH).iterdir():
            subprocess.run(["chmod", "+x", str(file)])

        result = subprocess.run(
            [
                "/usr/bin/pkgbuild",
                "--scripts", UNINSTALL_SCRIPT_PATH,
                "--identifier", "com.ripeda.privileges-client-uninstaller",
                "--version", self.version,
                "--install-location", "/", Path("Packaging/Uninstall-VPP-Detect.pkg"),
                "--nopayload"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode != 0:
            print("Failed to build uninstall pkg")
            print(result.stdout)
            print(result.stderr)
            exit(1)

    def _build_install_pkg(self) -> None:
        print("Building install pkg...")

        for file in Path(INSTALL_SCRIPT_PATH).iterdir():
            subprocess.run(["chmod", "+x", str(file)])

        if Path("vpp-detect").is_file():
            Path("vpp-detect").unlink()

        result = subprocess.run([
            "clang",
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

        # Create pkg directory structure
        Path("Packaging/Install/usr/local/bin").mkdir(parents=True, exist_ok=True)
        # Copy vpp-detect to pkg directory
        subprocess.run(["cp", "vpp-detect", "Packaging/Install/usr/local/bin/vpp-detect"])

        result = subprocess.run(
            [
                "/usr/bin/pkgbuild",
                "--scripts", INSTALL_SCRIPT_PATH,
                "--identifier", "com.ripeda.privileges-client-installer",
                "--version", self.version,
                "--install-location", "/", Path("Packaging/Install-VPP-Detect.pkg"),
                "--root", "Packaging/Install"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print("Failed to build install pkg")
            print(result.stdout)
            print(result.stderr)
            exit(1)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    Build()
    print("Done")
