"""Spike S2 (C-014, C-015): cross-check the expected values that frozen tests will assert
(DTC byte->code mapping, PID formulas) against python-OBD 0.7.3's independent decoders.
Every row printed here is pasted verbatim into tests/fixtures/expected_values.json.
"""
import json
from obd.decoders import parse_dtc
from obd.protocols.protocol import Message
from obd.protocols.protocol import Frame
import obd

def msg(data):
    f = Frame(""); f.data = bytearray(data)
    m = Message([f]); m.data = bytearray(data); return m

rows = {}
# DTC 2-byte encodings (SAE J2012 first-nibble rule)
for b in ["0133", "0420", "4123", "8001", "C155", "1234", "0000"]:
    rows["dtc_" + b] = parse_dtc(bytes.fromhex(b))
# PIDs: mode-01 response payloads WITHOUT the 41 xx prefix are what python-OBD decoders see after 2 bytes.
def dec(cmd, payload_hex):
    data = bytearray.fromhex("41" + cmd.command[2:].decode() + payload_hex)
    return cmd.decode([msg(data)])
cases = [(obd.commands.RPM, "1AF8"), (obd.commands.RPM, "0000"), (obd.commands.RPM, "FFFF"),
         (obd.commands.COOLANT_TEMP, "00"), (obd.commands.COOLANT_TEMP, "7B"), (obd.commands.COOLANT_TEMP, "FF"),
         (obd.commands.SPEED, "3C"), (obd.commands.THROTTLE_POS, "80"), (obd.commands.ENGINE_LOAD, "FF"),
         (obd.commands.INTAKE_TEMP, "3C"), (obd.commands.INTAKE_PRESSURE, "65"),
         (obd.commands.TIMING_ADVANCE, "80"), (obd.commands.CONTROL_MODULE_VOLTAGE, "3200"),
         (obd.commands.DISTANCE_W_MIL, "0102")]
for c, p in cases:
    v = dec(c, p)
    rows[f"pid_{c.command.decode()}_{p}"] = str(v)
# Monitor status PID 01: MIL bit and DTC count
st = dec(obd.commands.STATUS, "83076504")
rows["status_83076504"] = {"MIL": st.MIL, "DTC_count": st.DTC_count}
print(json.dumps(rows, indent=1, default=str))
