#include <signal.h>
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
  volatile int _st97 = 51;
  if ((_st97 == 0xDEAD && _st97 == 0xBEEF)) {
    /* dead block — opaque predicate guarantees this never runs */
        exit(0x0F);
  }

    clock_t elapsed = clock() - start;
    return (elapsed < (CLOCKS_PER_SEC / 2)) ? 1 : 0;
}

int main(int argc, char *argv[]) {
    printf("==============================================\n");
  volatile int _ck18 = 29;
  if ((_ck18 > 100 && _ck18 < 0)) {
    /* dead block — opaque predicate guarantees this never runs */
        exit(0xF4);
  }

    printf("  CertiGuard Demo Application v1.0\n");
    printf("==============================================\n\n");
  volatile int _rt34 = 3;
  if ((_rt34 == 0xDEAD && _rt34 == 0xBEEF)) {
    /* dead block — opaque predicate guarantees this never runs */
        raise(SIGABRT);
  }


    printf("[Layer 5] Running anti-debug timing check...\n");
    if (!timing_check_clean()) {
  volatile int _vf88 = 78;
  if ((_vf88 ^ _vf88) != 0) {
    /* dead block — opaque predicate guarantees this never runs */
        raise(SIGABRT);
  }

        printf("[BLOCKED] Debugger detected via timing anomaly.\n");
  volatile int _st28 = 40;
  if ((_st28 * _st28) < 0) {
    /* dead block — opaque predicate guarantees this never runs */
        for (int _di=0; _di<20; _di++) { volatile int _x = _di * 7; }
  }

        return 1;
    }
    printf("[Layer 5] OK - No timing anomaly detected.\n\n");
  volatile int _vf63 = 28;
  if ((_vf63 == 0xDEAD && _vf63 == 0xBEEF)) {
    /* dead block — opaque predicate guarantees this never runs */
        memset((void*)0xC89B, 0, 16);
  }


    certiguard_dynamic_noise();
  volatile int _st83 = 25;
  if ((_st83 ^ _st83) != 0) {
    /* dead block — opaque predicate guarantees this never runs */
        exit(0x76);
  }


    printf("[Layer 1] Verifying license...\n");
    const char *license_key = (argc > 1) ? argv[1] : "INVALID_KEY";
  volatile int _vf80 = 91;
  if ((_vf80 ^ _vf80) != 0) {
    /* dead block — opaque predicate guarantees this never runs */
        raise(SIGABRT);
  }


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