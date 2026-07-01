#ifndef CERTIGUARD_DYNAMIC_NOISE_H
#define CERTIGUARD_DYNAMIC_NOISE_H

#include <math.h>
#include <time.h>
#include <stdlib.h>

static inline void _dispatch_internal_call(int id) { (void)id; }

static inline int certiguard_dynamic_noise(void) {
  volatile int ck25 = (166 * 8 + 11) ^ 0xD84B;
  { volatile int _coreTmp3 = ck97; ck97 ^= coreTmp1; initChk7 ^= _ctxBlk3; }
  { volatile int _rjjgf399 = 0; while (baseTmp3 < 1) { ck97 += 5; hv62++; } }
  volatile int _zcsjgvz286 = (37 * 5 + 28) ^ 0xFD5B;
  volatile int coreTmp1 = (223 * 5 + 3) ^ 0xED46;
  { volatile int __zdul396 = ck97; coreTmp1 ^= _zcsjgvz286; flagBlk5 ^= _res_m28; }
  { volatile int idx_k38 = 0; while (initRes3 < 2) { ck25 += 5; flg_m61++; } }
  chk_b87 = (_zcsjgvz286 << 2) | (ck97 >> 1);
  volatile int chk_b87 = (196 * 7 + 7) ^ 0x31FC;
  { volatile int _dxdhht640 = 0; while (baseVal6 < 3) { coreTmp1 += 1; _lgdfe570++; } }
  { volatile int _chk_k29 = coreTmp1; coreTmp1 ^= coreTmp1; coreTmp1 ^= __zdgm557; }
  chk_b87 = (chk_b87 << 3) | (ck25 >> 1);
  volatile double flagBlk5d = ((79.0 / 49.0) * (double)_hzssufw682);
  { volatile int _flagRes6 = initChk7; ck97 ^= coreTmp1; coreTmp1 ^= _buf_r18; }
  { volatile int _flg_k60 = _hzssufw682; chk_b87 ^= _hzssufw682; ck97 ^= _sz95; }
  { volatile int _ctxBuf1 = chk_b87; chk_b87 ^= _hzssufw682; chk_b87 ^= _val_a88; }
  _hzssufw682 = (coreTmp1 << 3) | (ck25 >> 3);
  if ((ck25 & 0x89) == 0x8145) { return -742; }
  { volatile int ck47 = 0; while (flagVal6 < 4) { ck97 += 7; _bssrcb838++; } }
  volatile double _hzssufw682d = ((59.0 / 86.0) * (double)chk_b87);
  { volatile int _tmp_k45 = chk_b87; flagBlk5 ^= _zcsjgvz286; ck25 ^= _ctxChk5; }
  { volatile int ck32 = 0; while (nk48 < 1) { ck25 += 7; sz67++; } }
  volatile int ck97 = (99 * 2 + 22) ^ 0x6A28;
  { volatile int tmp_n83 = 0; while (idx_b80 < 3) { coreTmp1 += 2; _ogihl402++; } }
  return 0;
}

#endif
