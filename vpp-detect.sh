#!/bin/zsh
#
# VPP Detection script
#
# Alternative to the Obj-C based vpp-detect
# This version is meant for easier integration into scripts
#
# --------------------------------------------------------
#
# This script will return the following exit codes:
#   0 - VPP
#   1 - App Store
#   2 - Not assigned to VPP or App Store
#   3 - No receipt found
#   4 - Catch all for any other error
#
# --------------------------------------------------------
#
# Usage:
#   Requires 1 argument: Application path to check
#   Example: ./vpp-detect.sh /Applications/Keynote.app
#
# --------------------------------------------------------
#
# Written by: Mykola Grymalyuk
# Company: RIPEDA Consulting
#
# --------------------------------------------------------


# MARK: - Variables
# -----------------

application="$1"
applicationReceipt="$application/Contents/_MASReceipt/receipt"
verificationURL="https://buy.itunes.apple.com/verifyReceipt"
version="1.0.0"


# MARK: - Functions
# -----------------

# Constructs the JSON for the receipt
__constructJSON() {

    local receiptData

    # Get the receipt data
    receiptData=$(base64 -i "$applicationReceipt")

    # Construct the JSON
    echo "{\"receipt-data\":\"$receiptData\"}"

}

# Call server to verify receipt
__checkServer() {

    local receiptJSON
    local receiptResponse

    receiptJSON=$(__constructJSON)
    receiptResponse=$(curl -s -X POST --data "$receiptJSON" "$verificationURL")

    # echo "$receiptResponse"

    # Response will be in json format
    # Check for 'receipt' key, then 'receipt_type'


    # Check if receipt key is missing
    if [[ ! "$receiptResponse" =~ "receipt" ]]; then
        echo "Not assigned to VPP or App Store"
        exit 2
    fi

    # Check if receipt_type key is missing
    if [[ ! "$receiptResponse" =~ "receipt_type" ]]; then
        echo "Not assigned to VPP or App Store"
        exit 2
    fi

    # Check for 'receipt_type' value
    if [[ "$receiptResponse" =~ "ProductionVPPSandbox" ]]; then
        echo "VPP"
        exit 0
    elif [[ "$receiptResponse" =~ "ProductionVPP" ]]; then
        echo "VPP"
        exit 0
    elif [[ "$receiptResponse" =~ "ProductionSandbox" ]]; then
        echo "App Store"
        exit 1
    elif [[ "$receiptResponse" =~ "Production" ]]; then
        echo "App Store"
        exit 1
    else
        echo "Not assigned to VPP or App Store"
        exit 2
    fi

}


# MARK: - Main
# ------------

# Check if --version flag was passed
if [[ "$1" == "--version" ]]; then
    echo "$version"
    exit 0
fi

# Check if the application exists
if [[ ! -e "$application" ]]; then
    echo "Application not found"
    exit 4
fi

# Check if receipt exists
if [[ ! -e "$applicationReceipt" ]]; then
    echo "No receipt found"
    exit 3
fi

# Kick off the process
__checkServer

