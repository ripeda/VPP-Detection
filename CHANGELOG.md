# VPP Detection Changelog

## 1.1.0
- Switch to using macos-pkg-builder library for building the macOS package
  - Reduce file duplication (ie. `preinstall` scripts)
- Add signed and notarized executable and packages
  - Signed under `RIPEDA Consulting Corporation (2U3GKQ7U8Z)` Developer ID
  - Utilizes mac-signing-buddy library for signing and notarization
- Utilize full executable pathing in `vpp-detect.sh`
  - Avoids malformed pathing issues
- Add `-v` argument to `vpp-detect`/`vpp-detect.sh`
  - Shortened form of `--version`
- Add `--no-rcs` to all ZSH scripts
  - Avoids loading external settings

## 1.0.0
- Initial release