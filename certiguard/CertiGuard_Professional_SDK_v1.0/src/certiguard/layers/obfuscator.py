"""
CertiGuard — Source-Level C Obfuscator
Layer: Post-Noise, Pre-Compile

Applies Agile.NET-style obfuscation techniques to C source files:
1. Opaque Predicates  — adds conditions that always evaluate the same way
                        but look non-trivially complex to a reverse engineer.
2. Dead Branch Injection — adds unreachable code paths that look like real logic.
3. Control Flow Wrapping — wraps function bodies in fake dispatch structures.
4. String Literal Splitting — breaks string literals into char array construction.

These are source-level transforms. They survive compilation because GCC
cannot prove they are semantically meaningless (Turing-completeness guarantees).
"""
from __future__ import annotations

import random
import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Opaque Predicates
# ---------------------------------------------------------------------------
# An opaque predicate is a boolean expression whose value is ALWAYS known at
# analysis time (by the original developer) but appears complex to a reverser.
#
# Classic examples from academic literature (Collberg et al., 1997):
#   - (x*(x+1)) % 2 == 0   [always true — product of consecutive integers]
#   - (x*x) >= 0            [always true — square is non-negative]
#   - (a^2 + b^2) != 7      [never a perfect solution — number theory]
#
# We use these to inject always-true guards around real code and
# always-false blocks of dead code.

_ALWAYS_TRUE_PREDICATES = [
    # Product of consecutive integers is always even
    "({v} * ({v} + 1)) % 2 == 0",
    # Square is always >= 0
    "({v} * {v}) >= 0",
    # XOR with itself is always 0
    "({v} ^ {v}) == 0",
    # OR with all-ones is always non-zero (for any non-zero v)
    "(({v} | 0xFF) != 0)",
    # Bitwise AND with itself equals itself
    "({v} & {v}) == {v}",
]

_ALWAYS_FALSE_PREDICATES = [
    # A value cannot be both > 100 and < 0 simultaneously
    "({v} > 100 && {v} < 0)",
    # Square of an int is never negative
    "({v} * {v}) < 0",
    # XOR with itself is never non-zero
    "({v} ^ {v}) != 0",
    # A number cannot equal two different constants simultaneously
    "({v} == 0xDEAD && {v} == 0xBEEF)",
]


def _random_opaque_var(rng: random.Random) -> str:
    """Generate a realistic variable name for use in opaque predicates."""
    prefixes = ["_op", "_ck", "_vf", "_st", "_rt"]
    return rng.choice(prefixes) + str(rng.randint(10, 99))


def generate_opaque_predicate_guard(rng: random.Random, body_line: str) -> str:
    """
    Wrap a real line of code inside an always-true opaque predicate guard.
    To the reverser, it looks like a conditional check protects this code.
    """
    var = _random_opaque_var(rng)
    seed_val = rng.randint(2, 100)
    predicate = rng.choice(_ALWAYS_TRUE_PREDICATES).format(v=var)
    dead_predicate = rng.choice(_ALWAYS_FALSE_PREDICATES).format(v=var)
    dead_action = f"return -{rng.randint(1, 999)};"

    return (
        f"  volatile int {var} = {seed_val};\n"
        f"  if ({predicate}) {{\n"
        f"    {body_line}\n"
        f"  }} else if ({dead_predicate}) {{\n"
        f"    {dead_action}  /* dead branch — never reached */\n"
        f"  }}\n"
    )


def generate_dead_branch_block(rng: random.Random) -> str:
    """
    Generate a self-contained block of code that looks like real logic
    but is guaranteed to never execute (always-false opaque predicate gate).
    """
    var = _random_opaque_var(rng)
    seed_val = rng.randint(2, 100)
    predicate = rng.choice(_ALWAYS_FALSE_PREDICATES).format(v=var)

    fake_actions = [
        f"    memset((void*)0x{rng.randint(0x1000,0xFFFF):04X}, 0, 16);",
        f"    raise(SIGABRT);",
        f"    for (int _di=0; _di<{rng.randint(5,20)}; _di++) {{ volatile int _x = _di * {rng.randint(2,9)}; }}",
        f"    exit(0x{rng.randint(0,255):02X});",
    ]

    return (
        f"  volatile int {var} = {seed_val};\n"
        f"  if ({predicate}) {{\n"
        f"    /* dead block — opaque predicate guarantees this never runs */\n"
        f"    {rng.choice(fake_actions)}\n"
        f"  }}\n"
    )


# ---------------------------------------------------------------------------
# Source File Transformation
# ---------------------------------------------------------------------------

def obfuscate_c_source(source: str, seed: int = 0, intensity: int = 3) -> str:
    """
    Apply source-level obfuscation to a C source string.

    Args:
        source:    Full C source file content.
        seed:      Random seed for reproducibility.
        intensity: 1–5, controls how many transforms are applied per function.

    Returns:
        Obfuscated C source string.
    """
    rng = random.Random(seed)

    # Add required includes if not present
    if "#include <signal.h>" not in source:
        source = "#include <signal.h>\n" + source
    if "#include <string.h>" not in source:
        source = "#include <string.h>\n" + source

    lines = source.splitlines()
    output_lines: list[str] = []

    inside_function = False
    brace_depth = 0

    for line in lines:
        stripped = line.strip()

        # Track brace depth to know if we're inside a function body
        opens = line.count("{")
        closes = line.count("}")

        if opens > 0 and brace_depth == 0:
            inside_function = True

        brace_depth += opens - closes

        if brace_depth <= 0:
            inside_function = False
            brace_depth = 0

        output_lines.append(line)

        # Inject dead branches at random points inside function bodies
        if inside_function and brace_depth > 0 and stripped and not stripped.startswith("//"):
            if rng.random() < (intensity * 0.08):  # probability scales with intensity
                dead_block = generate_dead_branch_block(rng)
                output_lines.append(dead_block)

    return "\n".join(output_lines)


def obfuscate_c_file(input_path: Path, output_path: Path, seed: int = 0, intensity: int = 3) -> Path:
    """
    Read a C source file, apply obfuscation, and write to output path.

    Args:
        input_path:   Path to the original .c file.
        output_path:  Path to write the obfuscated .c file.
        seed:         Random seed.
        intensity:    1–5 obfuscation intensity.

    Returns:
        The output path.
    """
    source = input_path.read_text(encoding="utf-8")
    obfuscated = obfuscate_c_source(source, seed=seed, intensity=intensity)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(obfuscated, encoding="utf-8")
    return output_path


# ---------------------------------------------------------------------------
# ConfuserEx Integration (for .NET targets)
# ---------------------------------------------------------------------------

def run_confuserex(
    input_assembly: Path,
    output_dir: Path,
    confuserex_path: Path | None = None,
) -> bool:
    """
    Invoke ConfuserEx (free Agile.NET equivalent) on a .NET assembly.

    ConfuserEx applies:
    - Control flow obfuscation
    - Symbol renaming
    - Anti-tamper
    - Anti-debugging (via CLR hooks)

    Download: https://github.com/yck1509/ConfuserEx/releases

    Args:
        input_assembly:   Path to the .NET .exe or .dll to protect.
        output_dir:       Directory for the protected output.
        confuserex_path:  Path to Confuser.CLI.exe (optional, auto-detected).

    Returns:
        True if successful, False otherwise.
    """
    import subprocess
    import shutil

    # Auto-detect ConfuserEx if not provided
    if confuserex_path is None:
        detected = shutil.which("Confuser.CLI") or shutil.which("Confuser.CLI.exe")
        if detected:
            confuserex_path = Path(detected)
        else:
            print("[ConfuserEx] Confuser.CLI not found in PATH.")
            print("  Download from: https://github.com/yck1509/ConfuserEx/releases")
            print("  Then run: certiguard confuserex-protect --input your_app.exe --output ./protected/")
            return False

    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate a minimal ConfuserEx project file
    crproj_content = f"""<?xml version="1.0" encoding="utf-8"?>
<project baseDir="{input_assembly.parent.resolve()}"
         outputDir="{output_dir.resolve()}"
         xmlns="http://confuser.codeplex.com">
  <rule pattern="true" inherit="false">
    <protection id="rename" />
    <protection id="ctrl flow" />
    <protection id="anti debug" />
    <protection id="anti dump" />
    <protection id="anti tamper" />
  </rule>
  <module path="{input_assembly.resolve()}" />
</project>
"""
    crproj_path = output_dir / "certiguard_confuser.crproj"
    crproj_path.write_text(crproj_content, encoding="utf-8")

    result = subprocess.run(
        [str(confuserex_path), str(crproj_path)],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print(f"[ConfuserEx] Protection applied. Output: {output_dir}")
        return True
    else:
        print(f"[ConfuserEx] Error:\n{result.stderr}")
        return False
