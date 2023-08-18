/*
    Simple application to detect if the provided app bundle is a VPP-disributed app.

    Compile with:
        clang -framework Foundation -o vpp-detect vpp-detect.m
*/

#import <Foundation/Foundation.h>
#include <stdio.h>
#include <objc/objc.h>

typedef enum {
    VPP = 0,
    APP_STORE = 1,
    OS_APPLICATION = 2,
    NO_RECEIPT = 3,
    CATCH_ALL = 4
} ReturnCode;

#define VERIFCATION_URL "https://buy.itunes.apple.com/verifyReceipt"


int isVPPApp(NSString *path)
{
    /*
        Supported return codes:
        - 0: VPP
        - 1: App Store (user-purchased)
        - 2: OS Application (came with machine or downloded outside of App Store)
        - 3: No App Store receipt found
    */

    NSFileManager *fm = [NSFileManager defaultManager];
    NSString *receiptPath = [path stringByAppendingPathComponent:@"Contents/_MASReceipt/receipt"];

    if (![fm fileExistsAtPath:receiptPath]) {
        printf("No receipt found at %s\n", [receiptPath UTF8String]);
        return NO_RECEIPT;
    }

    NSData *receiptData = [NSData dataWithContentsOfFile:receiptPath];
    if (!receiptData) {
        printf("Unable to read receipt at %s\n", [receiptPath UTF8String]);
        return NO_RECEIPT;
    }

    NSError *error = nil;
    NSURL *url = [NSURL URLWithString:@VERIFCATION_URL];
    NSMutableURLRequest *request = [NSMutableURLRequest requestWithURL:url];
    [request setHTTPMethod:@"POST"];


    NSString *receiptDataString = [receiptData base64EncodedStringWithOptions:0];
    NSString *postString = [NSString stringWithFormat:@"{\"receipt-data\" : \"%@\"}", receiptDataString];
    NSData *postData = [postString dataUsingEncoding:NSUTF8StringEncoding];
    [request setHTTPBody:postData];

    // TODO: Switch to async request
    NSData *data = [NSURLConnection sendSynchronousRequest:request returningResponse:nil error:&error];
    if (error) {
        printf("Error: %s\n", [[error description] UTF8String]);
        return CATCH_ALL;
    }

    NSDictionary *results = [NSJSONSerialization JSONObjectWithData:data options:0 error:&error];

    // Check 'receipt' key
    if (![[results allKeys] containsObject:@"receipt"]) {
        printf("No receipt key found in response, likely OS application or distribution outside of App Store\n");
        return OS_APPLICATION;
    }

    // Check 'receipt' -> 'receipt_type' key
    NSDictionary *receipt = [results objectForKey:@"receipt"];
    if (![[receipt allKeys] containsObject:@"receipt_type"]) {
        printf("No receipt key found in response, likely OS application or distribution outside of App Store\n");
        return OS_APPLICATION;
    }

    /*
        Valid values:
            Production
            ProductionVPP
            ProductionSandbox
            ProductionVPPSandbox
    */
    NSString *receiptType = [receipt objectForKey:@"receipt_type"];
    printf("Receipt type: %s\n", [receiptType UTF8String]);
    if ([receiptType isEqualToString:@"ProductionVPP"] || [receiptType isEqualToString:@"ProductionVPPSandbox"]) {
        printf("Applicaton is VPP\n");
        return VPP;
    } else if ([receiptType isEqualToString:@"Production"] || [receiptType isEqualToString:@"ProductionSandbox"]) {
        printf("Applicaton is App Store\n");
        return APP_STORE;
    } else {
        printf("Applicaton is likely OS application or distribution outside of App Store\n");
        return OS_APPLICATION;
    }

    return 0;
}


int main(int argc, const char * argv[])
{
    @autoreleasepool {
        if (argc != 2) {
            printf("Usage: %s <path to app bundle>\n", argv[0]);
            return CATCH_ALL;
        }
        NSString *path = [NSString stringWithUTF8String:argv[1]];
        int result = isVPPApp(path);
        printf("Result: %d\n", result);
        return result;
    }
}