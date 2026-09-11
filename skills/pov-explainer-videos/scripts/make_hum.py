"""Generate a no-GPU ambient 'hum' drone WAV (stdlib only).
Usage: python3 make_hum.py out.wav [dur]
"""
import wave, struct, math, sys

SR = 44100
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 15.0
N = int(SR * DUR)

freqs = [52.0, 77.5, 104.0, 130.8]   # warm low hum stack
amps  = [0.40, 0.30, 0.22, 0.18]

def hum(t):
    v = 0.0
    for f, a in zip(freqs, amps):
        df = 0.7 * math.sin(2*math.pi*0.13*t)   # detune = living, organic hum
        v += a * math.sin(2*math.pi*(f+df)*t)
    trem = 0.7 + 0.3*math.sin(2*math.pi*0.35*t)  # breathing tremolo
    env  = min(1.0, t/1.5) * min(1.0, (DUR-t)/2.0)
    return v * trem * env

samples = [max(-1.0, min(1.0, hum(i/SR))) for i in range(N)]
pcm = b''.join(struct.pack('<h', int(s*32767)) for s in samples)

with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'hum.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm)
print('wrote', (sys.argv[1] if len(sys.argv) > 1 else 'hum.wav'), '%.1fs' % DUR)
