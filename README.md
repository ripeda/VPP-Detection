# VPP-Detection
Utility for detecting whether an application was distributed as VPP, user downloaded from the App Store or neither. Based on Apple's App Store verification system: [Validating receipts with the App Store](https://developer.apple.com/documentation/appstorereceipts/validating_receipts_with_the_app_store?language=objc)

* Offered either in Objective-C CLI application or ZSH script depending on your needs.
  * If unsure, Objective-C CLI application is recommended.
* Requires network access to Apple's servers.

----------

Compile (if using Objective-C CLI application):
```
clang -framework Foundation -o vpp-detect vpp-detect.m
```

Usage:
```
./vpp-detect <path to app bundle>
```

Application will return one of the following exit codes:
```
0 - VPP
1 - App Store
2 - Not assigned to VPP or App Store
3 - No receipt found
4 - Catch all for any other error
```

----------

Return code 2, `Not assigned to VPP or App Store`, means that the application has a Mac App Store receipt however is not associated with VPP or an iCloud account. This is generally the case for applications that shipped with the OS, and will be assigned to an iCloud user after setup. Sample applications include:
* GarageBand
* iMovie
* Keynote
* Numbers
* Pages

Same applies for Pro App Bundles, however this needs to be purchased along side the Mac. Sample applications include:
* Final Cut Pro
* Logic Pro
* Motion
* Compressor
* MainStage