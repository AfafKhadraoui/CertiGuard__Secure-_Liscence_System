# 🎙️ CertiGuard™ Demo Walkthrough Guide

Use this script to explain the demo to the judges. Every step corresponds to a requirement in **Problématique N°2**.

## 🚀 Introduction (The Problem)
> "Our goal is to protect on-premise software from being tampered with. Currently, a client can often just edit a configuration file to increase their user limit. CertiGuard™ makes that impossible."

## 🛠️ Step 1: The Build (Polymorphism)
**Action**: Run `.\PROVE_SECURITY.ps1`
> "We don't just compile the app. We use our **VM Generator** to create a custom language for this build. Even if a hacker has a decompiler, they can't read this logic because it's not standard x86—it's **CertiGuard Virtual Machine** code."

## 🧪 Step 2: Normal Operation (The Barrier)
> "Notice the app runs in 'Trial' mode by default. The security logic is already checking for a license, but it's doing it silently using **Anti-Debug timing** to ensure no one is watching."

## 🔨 Step 3: Attack 1 - Falsification (Integrity)
> "Now, imagine the client tries to change '5 Users' to '500 Users' in the license file. Our SDK uses **Ed25519 Cryptographic Signatures**. If even one bit of the license is changed, the **Integrity Layer** detects it instantly and locks the app. The parameters cannot be falsified."

## 🧬 Step 4: Attack 2 - Cloning (DNA Binding)
> "What if they try to copy a valid license to another machine? Our **Hardware DNA** layer scans the motherboard serial and CPU ID. If the DNA doesn't match the one 'Stamped' in the license, the software refuses to decrypt. It is physically bound to the machine."

## 🌑 Step 5: Attack 3 - Reverse Engineering (Obfuscation)
> "Finally, a hacker might try to find the 'Success' messages or 'Keys' inside the binary. As you see, our **XOR String Encryption** hides all text. The binary is a 'Black Box'."

---

## 🏆 Final Conclusion (The Deliverable)
> "In an on-premise environment with no internet, CertiGuard™ provides a **Root of Trust** that cannot be bypassed by editing files, cloning machines, or using debuggers. We have solved the problem of license parameter integrity."
