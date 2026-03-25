# KubeSecMaaz 🛡️
**Custom Security R&D Tool by Maaz Adhoni**

## Concept
KubeSecMaaz is an automated validation framework built during Security R&D to test the effectiveness of Kubernetes hardening. It assumes an application-level breach (RCE) has occurred and tests if the **infrastructure** can stop the attacker's progression.

## Attack Logic Integrated
This tool consolidates 11 specific attack vectors derived from intensive research:
* **Information Leakage:** Metadata API access and K8s API enumeration.
* **Privilege Escalation:** Checking for dangerous capabilities and host-level filesystem escapes.
* **Container Escape:** Validating if the `nsenter` or socket-mounting techniques are blocked.
* **Runtime Maliciousness:** Detecting reverse shells and lateral movement attempts.

## Hardening Targets
KubeSecMaaz is designed to be "defeated" by the following controls:
1. **NetworkPolicy:** To block IMDS and Egress.
2. **Kyverno/PSS:** To block Privileged pods and HostPath mounts.
3. **Tetragon (eBPF):** To kill reverse shells and miners at the kernel level.
4. **Istio mTLS:** To prevent unauthorized pod-to-pod communication.

## Quick Start
```bash
python3 kubesecmaaz.py --url http://<target-endpoint>/debug/
