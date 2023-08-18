import os
import subprocess

from pathlib import Path

RETURN_CODES = {
    "VPP": 0,
    "APP_STORE": 1,
    "OS_APPLICATION": 2,
    "NO_RECEIPT": 3,
    "CATCH_ALL": 4,
}

TEST_SUITE = {
    "./Test Suite/iLife (OS Shipped)": {
        "Expected": RETURN_CODES["OS_APPLICATION"],
        "Apps": {
            "Pages.app",
            "Keynote.app",
            "Numbers.app",
        },
    },
    "./Test Suite/iLife (User owned)": {
        "Expected": RETURN_CODES["APP_STORE"],
        "Apps": {
            "Pages.app",
            "Keynote.app",
            "Numbers.app",
        },
    },
}

CLI_PATH = "./vpp-detect"
os.chdir(os.path.dirname(os.path.realpath(__file__)))

class Validate:

    def __init__(self, app: str) -> None:
        self.app = app
        self._is_cli_installed()

    def _is_cli_installed(self) -> None:
        if Path(CLI_PATH).is_file():
            return
        print("vpp-detect not found, compiling...")
        result = subprocess.run(["clang", "-framework", "Foundation", "-o", "vpp-detect", "vpp-detect.m"], capture_output=True)
        if result.returncode != 0:
            print("Failed to compile vpp-detect")
            exit(1)

    def run(self) -> int:
        result = subprocess.run([CLI_PATH, self.app], capture_output=True)
        return_code = result.returncode
        return return_code


if __name__ == "__main__":
    for suite in TEST_SUITE:
        print(f"Testing {suite}")
        for app in TEST_SUITE[suite]["Apps"]:
            print(f"  Testing {app}")
            path = os.path.join(suite, app)
            validate = Validate(path)
            return_code = validate.run()
            if return_code == TEST_SUITE[suite]["Expected"]:
                print(f"    PASS: {app} in {suite}")
            else:
                print(f"FAIL: {app} in {suite}")
                print(f"Expected: {TEST_SUITE[suite]['Expected']}")
                print(f"Received: {return_code}")
                exit(1)