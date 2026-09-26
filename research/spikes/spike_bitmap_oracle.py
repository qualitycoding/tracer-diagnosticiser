"""Spike S4 (C-015): supported-PID bitmap decoding oracle via python-OBD 0.7.3 (PIDS_A decoder)."""
import obd
from obd.protocols.protocol import Frame, Message
def dec(cmd, payload_hex):
    data = bytearray.fromhex("4100" + payload_hex)
    f = Frame(""); f.data = data; m = Message([f]); m.data = data
    return cmd.decode([m])
for bm in ("BE1FA813", "983B8013", "00000000", "FFFFFFFF"):
    bits = dec(obd.commands.PIDS_A, bm)
    print(bm, sorted(hex(i + 1) for i, b in enumerate(bits) if b))
