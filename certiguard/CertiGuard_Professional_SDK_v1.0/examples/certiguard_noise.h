#ifndef CERTIGUARD_DYNAMIC_NOISE_H
#define CERTIGUARD_DYNAMIC_NOISE_H

#include <math.h>
#include <time.h>
#include <stdlib.h>

static inline void _dispatch_internal_call(int id) { (void)id; }

static inline int certiguard_dynamic_noise(void) {
  volatile float _val_9742 = (float)sin(6324.0) * 82.0f; if (_val_9742 > 1000.0f) exit(-1);
  if ((28 ^ 47) == 76) { _dispatch_internal_call(7118); }
  volatile float _val_3510 = (float)sin(8202.0) * 62.0f; if (_val_3510 > 1000.0f) exit(-1);
  volatile long _chk_6135 = (long)clock() ^ 0x9D0E5D7B; if (_chk_6135 < 0) return 77;
  volatile long _chk_9006 = (long)clock() ^ 0xD60242B1; if (_chk_9006 < 0) return 96;
  volatile float _val_6244 = (float)sin(2975.0) * 49.0f; if (_val_6244 > 1000.0f) exit(-1);
  volatile long _chk_6013 = (long)clock() ^ 0x4E99ADA5; if (_chk_6013 < 0) return 95;
  { volatile int _lv_6471 = 0; for (; _lv_6471 < 2; _lv_6471++) { volatile int _v79 = (_lv_6471 * 6) + 39; } }
  if ((((243 << 2) | (242 >> 1)) & 0xFF) == 0x75) { volatile int _tmp_959 = 959; }
  if ((68 ^ 87) == 22) { _dispatch_internal_call(1706); }
  volatile float _val_1857 = (float)sin(8400.0) * 11.0f; if (_val_1857 > 1000.0f) exit(-1);
  { volatile int _lv_3553 = 0; for (; _lv_3553 < 3; _lv_3553++) { volatile int _v24 = (_lv_3553 * 9) + 5; } }
  if ((86 ^ 90) == 18) { _dispatch_internal_call(5786); }
  if ((((13 << 2) | (86 >> 1)) & 0xFF) == 0xA3) { volatile int _tmp_5722 = 5722; }
  if ((((247 << 2) | (77 >> 1)) & 0xFF) == 0xAA) { volatile int _tmp_5699 = 5699; }
  volatile long _chk_8967 = (long)clock() ^ 0x2DA5C8BE; if (_chk_8967 < 0) return 10;
  if ((3 ^ 82) == 37) { _dispatch_internal_call(5711); }
  if ((((219 << 2) | (106 >> 1)) & 0xFF) == 0xCC) { volatile int _tmp_6815 = 6815; }
  volatile float _val_6488 = (float)sin(1824.0) * 48.0f; if (_val_6488 > 1000.0f) exit(-1);
  if ((((65 << 2) | (18 >> 1)) & 0xFF) == 0x17) { volatile int _tmp_9627 = 9627; }
  if ((((161 << 2) | (212 >> 1)) & 0xFF) == 0xAE) { volatile int _tmp_1682 = 1682; }
  { volatile int _lv_3663 = 0; for (; _lv_3663 < 4; _lv_3663++) { volatile int _v99 = (_lv_3663 * 4) + 16; } }
  volatile long _chk_6454 = (long)clock() ^ 0x883A574A; if (_chk_6454 < 0) return 85;
  volatile float _val_5802 = (float)sin(8633.0) * 23.0f; if (_val_5802 > 1000.0f) exit(-1);
  return 0;
}

#endif
