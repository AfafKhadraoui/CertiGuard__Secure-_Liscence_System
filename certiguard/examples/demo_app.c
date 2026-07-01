#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "certiguard_noise.h"
#include "certiguard_vm.h"

#define EXPECTED_LICENSE_HASH "a3f9c2d8e1b4f7a9"

static int real_license_check(const char *license_key) {
    unsigned char input_val = (unsigned char)license_key[0];
    return certiguard_vm_execute(input_val);
}

static int timing_check_clean(void) {
    clock_t start = clock();
    volatile long dummy = 0;
    for (int i = 0; i < 500000; i++) dummy += i;
    clock_t elapsed = clock() - start;
    return (elapsed < (CLOCKS_PER_SEC / 2)) ? 1 : 0;
}

int main(int argc, char *argv[]) {
    printf("==============================================\n");
    printf("  CertiGuard Demo Application v1.0\n");
    printf("==============================================\n\n");

    printf("[Layer 5] Running anti-debug timing check...\n");
    if (!timing_check_clean()) {
        printf("[BLOCKED] Debugger detected via timing anomaly.\n");
        return 1;
    }
    printf("[Layer 5] OK - No timing anomaly detected.\n\n");

    certiguard_dynamic_noise();

    printf("[Layer 1] Verifying license...\n");
    const char *license_key = (argc > 1) ? argv[1] : "INVALID_KEY";

    if (!real_license_check(license_key)) {
        printf("[BLOCKED] Invalid license key: %s\n", license_key);
        printf("          Usage: demo_app.exe a3f9c2d8\n");
        return 1;
    }

    printf("[Layer 1] License verified successfully.\n\n");
    printf("==============================================\n");
    printf("  Application running. All layers passed.\n");
    printf("==============================================\n");
    return 0;
}
