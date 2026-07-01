import pytest
from certiguard.layers.obfuscator import obfuscate_c_file

def test_c_source_obfuscation_logic():
    """
    Verifies that the obfuscator correctly encrypts strings and 
    injects opaque predicates into C source code.
    """
    original_code = """
    #include <stdio.h>
    int main() {
        printf("Hello World");
        return 0;
    }
    """
    
    # Run the obfuscator
    obfuscated_code = obfuscate_c_file(original_code, seed=42, intensity=5)
    
    # PROOF 1: The original string "Hello World" must be GONE
    assert "Hello World" not in obfuscated_code
    
    # PROOF 2: The decryption helper must be present
    assert "certiguard_decrypt_str" in obfuscated_code
    
    # PROOF 3: The XOR-encrypted version must exist (hex data)
    assert "\\x" in obfuscated_code
    
    # PROOF 4: Opaque Predicates (the Maze) must be injected
    assert "_rt" in obfuscated_code
    assert "volatile int" in obfuscated_code
    
    print("\n[SUCCESS] Obfuscation validation passed. Strings are encrypted and predicates injected.")

if __name__ == "__main__":
    test_c_source_obfuscation_logic()
