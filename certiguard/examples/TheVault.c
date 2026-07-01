#include <stdio.h>
#include <string.h>
#include "certiguard_noise.h"
#include "certiguard_vm.h"

// This function represents your most sensitive intellectual property
void access_secret_vault() {
    printf("\n[ACCESS GRANTED] Decrypting the Master Corporate Database...\n");
    printf(">> Loading Sector 7G Data...\n");
    printf(">> SECRETS LOADED SUCCESSFULLY.\n\n");
}

int main(int argc, char *argv[]) {
    // Layer 5: Active Anti-Debug Sentry
    certiguard_dynamic_noise();

    printf("==============================================\n");
    printf("   CERTIGUARD™ SECURE VAULT v4.0\n");
    printf("==============================================\n");

    // The Challenge: Only the CertiGuard VM can solve this
    int challenge_token = (argc > 1) ? atoi(argv[1]) : 0;
    
    if (certiguard_vm_execute(challenge_token)) {
        access_secret_vault();
    } else {
        printf("[ACCESS DENIED] Security Integrity Check Failed.\n");
        printf("Please ensure your Hardware DNA matches the license.\n");
        return 1;
    }

    return 0;
}
