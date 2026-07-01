from __future__ import annotations

import random
from pathlib import Path


def _random_varname(rng: random.Random) -> str:
    """Generate a realistic-looking variable name with no predictable prefix."""
    # Mix of naming styles real programmers use — defeats pattern-matching filters
    styles = [
        # Short cryptic names (looks like real low-level C)
        lambda: rng.choice(["rc", "st", "ck", "fl", "vk", "sz", "nk", "hv"])
                + str(rng.randint(1, 99)),
        # snake_case (looks like internal validation helpers)
        lambda: rng.choice(["chk", "val", "res", "tmp", "buf", "flg", "idx", "off"])
                + "_" + rng.choice(["a", "b", "x", "y", "n", "k", "m", "r"])
                + str(rng.randint(10, 99)),
        # camelCase (looks like a field or property name)
        lambda: rng.choice(["init", "base", "core", "flag", "mask", "hash", "key", "ctx"])
                + rng.choice(["Val", "Buf", "Res", "Tmp", "Chk", "Blk"])
                + str(rng.randint(1, 9)),
        # Fully opaque (looks like a compiler-generated symbol)
        lambda: "_" + "".join(rng.choice("abcdefghijklmnopqrstuvwxyz")
                               for _ in range(rng.randint(4, 7)))
                + str(rng.randint(100, 999)),
    ]
    return rng.choice(styles)()


def generate_rule_noise_block(rng: random.Random, lines: int = 24) -> str:
    # Generate a pool of realistic variable names up front — then reuse them,
    # just like real code does. This defeats "only referenced once" heuristics.
    pool = [_random_varname(rng) for _ in range(8)]

    ops = [
        # Integer XOR with realistic-looking hex constant
        lambda: (
            f"volatile int {rng.choice(pool)} = "
            f"({rng.randint(1,255)} * {rng.randint(2,13)} + {rng.randint(1,31)}) "
            f"^ 0x{rng.getrandbits(16):04X};"
        ),
        # Loop using a pooled variable (variable reuse — looks like a real loop counter)
        lambda: (
            f"{{ volatile int {_random_varname(rng)} = 0; "
            f"while ({_random_varname(rng)} < {rng.randint(1,4)}) "
            f"{{ {rng.choice(pool)} += {rng.randint(1, 7)}; "
            f"{_random_varname(rng)}++; }} }}"
        ),
        # Double-precision computation (looks like a floating-point integrity check)
        lambda: (
            f"volatile double {rng.choice(pool)}d = "
            f"(({rng.randint(1,90)}.0 / {rng.randint(2,99)}.0) "
            f"* (double){rng.choice(pool)});"
        ),
        # Always-false guard (looks like a real overflow/bounds check)
        lambda: (
            f"if (({rng.choice(pool)} & 0x{rng.getrandbits(8):02X}) == "
            f"0x{rng.getrandbits(16):04X}) {{ return -{rng.randint(1,999)}; }}"
        ),
        # Bitshift assignment (looks like a real state machine transition)
        lambda: (
            f"{rng.choice(pool)} = ({rng.choice(pool)} << {rng.randint(1,3)}) "
            f"| ({rng.choice(pool)} >> {rng.randint(1,4)});"
        ),
        # Variable swap (looks like real crypto key mixing)
        lambda: (
            f"{{ volatile int _{_random_varname(rng)} = {rng.choice(pool)}; "
            f"{rng.choice(pool)} ^= {rng.choice(pool)}; "
            f"{rng.choice(pool)} ^= _{_random_varname(rng)}; }}"
        ),
    ]
    return "\n".join(rng.choice(ops)() for _ in range(lines))



def generate_smart_noise_block(rng: random.Random, lines: int = 24) -> str:
    """AI-inspired noise that looks like real validation logic."""
    templates = [
        "if (((({a} << 2) | ({b} >> 1)) & 0xFF) == 0x{c:02X}) {{ volatile int _tmp_{d} = {d}; }}",
        "volatile long _chk_{id} = (long)clock() ^ 0x{key:08X}; if (_chk_{id} < 0) return {ret};",
        "{{ volatile int _lv_{id} = 0; for (; _lv_{id} < {count}; _lv_{id}++) {{ volatile int {var} = (_lv_{id} * {mul}) + {add}; }} }}",
        "volatile float _val_{id} = (float)sin({seed}.0) * {scale}.0f; if (_val_{id} > 1000.0f) exit(-1);",
        "if (({p1} ^ {p2}) == {p3}) {{ _dispatch_internal_call({id}); }}",
    ]
    
    block = []
    for _ in range(lines):
        t = rng.choice(templates)
        block.append(t.format(
            a=rng.randint(1, 255), b=rng.randint(1, 255), c=rng.randint(1, 255), d=rng.randint(1, 9999),
            id=rng.randint(1000, 9999), key=rng.getrandbits(32), ret=rng.randint(1, 100),
            count=rng.randint(2, 5), var=f"_v{rng.randint(1,99)}", mul=rng.randint(2, 10), add=rng.randint(1, 50),
            seed=rng.randint(1, 10000), scale=rng.randint(10, 100),
            p1=rng.randint(1, 100), p2=rng.randint(1, 100), p3=rng.randint(1, 100)
        ))
    return "\n".join(block)


def generate_polymorphic_noise_block(rng: random.Random, lines: int = 24) -> str:
    """Noise where variables and operations change roles randomly."""
    roles = ["state", "buffer", "key", "nonce", "counter"]
    vars_map = {role: f"_poly_{role}_{rng.randint(10,99)}" for role in roles}
    
    preamble = [f"volatile long {v} = {rng.getrandbits(16)};" for v in vars_map.values()]
    
    ops = [
        lambda: f"{vars_map['state']} = ({vars_map['state']} ^ {vars_map['key']}) + {rng.randint(1,100)};",
        lambda: f"{vars_map['buffer']} = ({vars_map['buffer']} << {rng.randint(1,3)}) | {vars_map['nonce']};",
        lambda: f"if ({vars_map['counter']}++ > {rng.randint(10,100)}) {{ {vars_map['key']} ^= {vars_map['state']}; }}",
        lambda: f"{vars_map['nonce']} = ({vars_map['nonce']} * {rng.randint(3,7)}) ^ {vars_map['buffer']};",
    ]
    
    body = [rng.choice(ops)() for _ in range(lines)]
    return "\n".join(preamble + body)


def generate_noise_header(seed: int, out_path: Path, mode: str = "rule", lang: str = "c", lines: int = 24) -> Path:
    rng = random.Random(seed)
    
    if mode == "rule":
        body = generate_rule_noise_block(rng, lines)
    elif mode == "smart":
        body = generate_smart_noise_block(rng, lines)
    elif mode == "polymorphic":
        body = generate_polymorphic_noise_block(rng, lines)
    else:
        raise ValueError(f"Unknown noise mode: {mode}")

    if lang == "c":
        content = (
            "#ifndef CERTIGUARD_DYNAMIC_NOISE_H\n"
            "#define CERTIGUARD_DYNAMIC_NOISE_H\n\n"
            "#include <math.h>\n"
            "#include <time.h>\n"
            "#include <stdlib.h>\n\n"
            "static inline void _dispatch_internal_call(int id) { (void)id; }\n\n"
            "static inline int certiguard_dynamic_noise(void) {\n"
            f"{chr(10).join('  ' + line for line in body.splitlines())}\n"
            "  return 0;\n"
            "}\n\n"
            "#endif\n"
        )
    elif lang == "csharp":
        # Convert C-style noise to C# style (simple replacements)
        cs_body = body.replace("volatile int", "int") # C# volatile is different, usually unnecessary for noise
        cs_body = cs_body.replace("volatile double", "double")
        cs_body = cs_body.replace("volatile float", "float")
        cs_body = cs_body.replace("volatile long", "long")
        cs_body = cs_body.replace("(float)sin", "(float)Math.Sin")
        cs_body = cs_body.replace("(long)clock()", "DateTime.Now.Ticks")
        cs_body = cs_body.replace("exit(-1);", "Environment.Exit(-1);")
        
        content = (
            "using System;\n\n"
            "namespace CertiGuard.Generated {\n"
            "    public static class DynamicNoise {\n"
            "        private static void _dispatch_internal_call(int id) { }\n\n"
            "        public static int Execute() {\n"
            f"{chr(10).join('            ' + line for line in cs_body.splitlines())}\n"
            "            return 0;\n"
            "        }\n"
            "    }\n"
            "}\n"
        )
    else:
        raise ValueError(f"Unknown language: {lang}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    return out_path

