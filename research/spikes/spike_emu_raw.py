import os, subprocess, sys, tempfile, time, serial
out = tempfile.mktemp()
p = subprocess.Popen([sys.executable, "-m", "elm", "-s", "car", "-b", out], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(100):
    if os.path.exists(out) and open(out).read().strip(): break
    time.sleep(0.1)
s = serial.Serial(open(out).readline().strip(), 38400, timeout=2)
def q(c):
    s.write((c + "\r").encode()); buf = b""
    while not buf.endswith(b">"):
        ch = s.read(1)
        if not ch: break
        buf += ch
    print(repr(c), "->", repr(buf.decode()))
for c in ["ATZ","ATE0","ATL0","ATS1","ATH1","ATSP0","ATRV","0100","ATDPN","ATDP","0902","03","010C"]:
    q(c)
p.terminate()
