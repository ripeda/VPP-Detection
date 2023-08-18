# VPP-Detection
Objective-C based utility for detecting whether an application was distributed as VPP, user downloaded from the App Store or neither.

----------

Compile:
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

Return code 3, `Not assigned to VPP or App Store`, means that the application has a Mac App Store receipt however is not associated with VPP or an iCloud account. This is generally the case for applications that shipped with the OS, and will be assigned to an iCloud user after setup. Sample applications include:
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