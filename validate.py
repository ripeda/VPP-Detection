import os
import subprocess

from pathlib import Path

RETURN_CODES: dict = {
    "VPP": 0,
    "APP_STORE": 1,
    "OS_APPLICATION": 2,
    "NO_RECEIPT": 3,
    "CATCH_ALL": 4,
}

TEST_SUITE: dict = {
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
    "./Test Suite/iLife (VPP)": {
        "Expected": RETURN_CODES["VPP"],
        "Apps": {
            "Pages.app",
            "Keynote.app",
            "Numbers.app",
        },
    },
}

CLI_PATH:    str = "./vpp-detect"
SCRIPT_PATH: str = "./vpp-detect.sh"

os.chdir(os.path.dirname(os.path.realpath(__file__)))

class Validate:

    def __init__(self, tool: str, app: str) -> None:
        self.tool = tool
        self.app = app
        self._is_cli_installed()

    def _is_cli_installed(self) -> None:
        if Path(self.tool).is_file():
            return
        if self.tool != CLI_PATH:
            raise Exception("Script not found")

        print("vpp-detect not found, compiling...")
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

    def run(self) -> int:
        result = subprocess.run([self.tool, self.app], capture_output=True)
        return_code = result.returncode
        return return_code


if __name__ == "__main__":
    for tool in [CLI_PATH, SCRIPT_PATH]:
        print(f"Testing {tool}")
        for suite in TEST_SUITE:
            print(f"  Testing {suite}")
            for app in TEST_SUITE[suite]["Apps"]:
                print(f"    Testing {app}")
                path = os.path.join(suite, app)
                validate = Validate(tool, path)
                return_code = validate.run()
                if return_code == TEST_SUITE[suite]["Expected"]:
                    print(f"      PASS: {app} in {suite}")
                else:
                    print(f"      FAIL: {app} in {suite}")
                    print(f"      Expected: {TEST_SUITE[suite]['Expected']}")
                    print(f"      Received: {return_code}")
                    exit(1)