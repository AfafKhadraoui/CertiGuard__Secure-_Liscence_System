/* 
 * CertiGuard Industrial Sentinel v2.5
 * (C) 2026 Industrial Systems Corp.
 * 
 * This application simulates a high-value industrial control system.
 * Protected by CertiGuard™ Enterprise SDK.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "certiguard_noise.h"
#include "certiguard_vm.h"

// Realistic Industrial Modules
typedef struct {
    int max_sensors;
    int heater_control_enabled;
    int database_export_enabled;
    char license_tier[32];
} AppCapabilities;

// This is our "Protected Logic"
void run_industrial_process(AppCapabilities caps) {
    printf("\n--- SYSTEM STATUS ---\n");
    printf("Tier: %s\n", caps.license_tier);
    printf("Active Sensors: %d / %d\n", (caps.max_sensors > 0 ? 5 : 0), caps.max_sensors);
    
    if (caps.heater_control_enabled) {
        printf("[MODULE] Heater Control: ONLINE\n");
    } else {
        printf("[MODULE] Heater Control: DISABLED (Upgrade Required)\n");
    }

    if (caps.database_export_enabled) {
        printf("[MODULE] Data Export: READY\n");
    } else {
        printf("[MODULE] Data Export: DISABLED (Upgrade Required)\n");
    }
    printf("---------------------\n\n");
}

int main(int argc, char *argv[]) {
    // 1. Initial SDK Security Layers
    certiguard_dynamic_noise();

    // 2. Mocking the capability extraction (in a real app, this comes from the SDK's decrypted manifest)
    // For this demo, we simulate the logic that the SDK would verify.
    AppCapabilities my_caps = {0, 0, 0, "UNAUTHORIZED"};

    printf("==============================================\n");
    printf("  INDUSTRIAL SENTINEL - CONTROL DASHBOARD\n");
    printf("==============================================\n");
    
    // The "VM Security Check" — This is the core of Problématique N°2
    // We pass a 'Challenge' to the VM. Only a valid license holder can solve it.
    int security_token = (argc > 1) ? atoi(argv[1]) : 0;
    
    if (certiguard_vm_execute(security_token)) {
        // If VM returns true, we enable "Enterprise" features
        my_caps.max_sensors = 100;
        my_caps.heater_control_enabled = 1;
        my_caps.database_export_enabled = 1;
        strcpy(my_caps.license_tier, "ENTERPRISE GOLD");
    } else {
        // Limited "Standard" mode
        my_caps.max_sensors = 5;
        my_caps.heater_control_enabled = 0;
        my_caps.database_export_enabled = 0;
        strcpy(my_caps.license_tier, "STANDARD (TRIAL)");
    }

    run_industrial_process(my_caps);

    if (strcmp(my_caps.license_tier, "UNAUTHORIZED") == 0) {
        return 1;
    }

    return 0;
}
