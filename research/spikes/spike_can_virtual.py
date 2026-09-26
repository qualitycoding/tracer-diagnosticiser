"""Spike S3 (C-017): python-can 4.6.1 virtual bus round-trip + slcan listen_only parameter exists.
Validates that a passive-capture tool can be unit-tested without hardware (virtual interface)
and that SlcanBus exposes listen_only (sends 'L' open command instead of 'O').
"""
import inspect, can
from can.interfaces.slcan import slcanBus
a = can.Bus(interface="virtual", channel="t"); b = can.Bus(interface="virtual", channel="t")
a.send(can.Message(arbitration_id=0x7E8, data=bytes.fromhex("03410C1AF8AAAAAA"), is_extended_id=False))
m = b.recv(1.0); print("virtual rx:", hex(m.arbitration_id), m.data.hex())
print("slcan listen_only param:", "listen_only" in inspect.signature(slcanBus.__init__).parameters)
src = inspect.getsource(slcanBus.open); print("slcan open uses 'L' when listen_only:", '"L"' in src or "'L'" in src)
a.shutdown(); b.shutdown()
