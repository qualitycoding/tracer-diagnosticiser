"""Spike S1 (C-012, C-013): python-OBD 0.7.3 talks ISO 15765-4 CAN via an ELM327 command set.

Runs ELM327-emulator 4.0.0 in batch mode on a pseudo-tty (scenario 'car', CAN 11-bit
500 kbaud), then uses python-OBD to (a) auto-detect the protocol, (b) read RPM and
coolant temperature, (c) read stored DTCs, (d) confirm the raw ATDPN protocol number.
Throwaway research code; not part of the deliverable.
"""
import os, subprocess, sys, tempfile, time
import obd

out = tempfile.mktemp()
proc = subprocess.Popen([sys.executable, "-m", "elm", "-s", "car", "-b", out],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(100):
        if os.path.exists(out) and open(out).read().strip():
            break
        time.sleep(0.1)
    port = open(out).readline().strip()
    print("emulator pty:", port)
    conn = obd.OBD(port, fast=False, timeout=5)
    print("status:", conn.status())
    print("protocol:", conn.protocol_id(), conn.protocol_name())
    for cmd in (obd.commands.RPM, obd.commands.COOLANT_TEMP, obd.commands.GET_DTC,
                obd.commands.ELM_VOLTAGE):
        r = conn.query(cmd)
        print(f"{cmd.name}: {r.value!r}")
    conn.close()
finally:
    proc.terminate(); proc.wait(timeout=5)
