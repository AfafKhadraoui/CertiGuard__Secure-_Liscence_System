# CertiGuard Development Methodology

## 1. The "Iterative Hardening" Approach
Our development followed a cyclical process designed to ensure that every security layer actually provides value:

1.  **Requirement Mapping**: Aligning with the 10-layer "Prevention + Detection + Forensics" framework.
2.  **Implementation**: Writing the core Python/C logic for a layer (e.g., Anti-Debug).
3.  **Red-Team Validation**: Attempting to bypass the layer using tools like `GDB`, `x64dbg`, and `Ghidra`.
4.  **Feedback Loop**: Improving the layer (e.g., adding "Noise" to mask the Anti-Debug logic).

## 2. Technology Stack Selection
*   **Python (The Architect)**: Used for the build-time generation engine because of its flexibility in handling complex data (ISA generation, noise templates).
*   **C/C++ (The Payload)**: Used for the runtime security layers to ensure maximum performance and low-level hardware access (TPM, RAM probing).
*   **React/Flask (The Dashboard)**: Chosen for high-speed data visualization and real-time event streaming.

## 3. Quality Assurance & Testing
*   **E2E Harness**: We created a full end-to-end "Harness" (`run_harness.py`) that simulates a year of usage in 10 seconds.
*   **Violation Demo**: A dedicated "Attack Simulator" that verifies the dashboard accurately reflects complex threats like "Honeypot" and "Tamper" events.
