"""Original score for the GSS pitch video, synthesized from scratch (no samples, no licensing).

A minor, 100 BPM, 48 bars (115.2 s) + 0.8 s tail = 116 s. Cues (bar numbers are 1-based):
  1-12  calm: drone, clock ticks, sparse plucks, bass enters at 7, soft kick at 11
  13-20 build: Am-F-C-G arpeggio with a rising filter, drums thicken, snare roll + riser in 20
  21-28 DROP (Claude finds time zero): full groove
  29-32 tension: drums out, dark drone, louder clock, heartbeat
  33    STING (Flash, 46 ps off), 33-34 dark hold
  35-38 rebuild: half-time groove, arpeggio returns
  39-45 final lift: full groove
  46-48 resolve: drums out, final chord rings and fades

    uv run --no-project --with numpy --with scipy python video/v2/music.py   -> video/v2/score.wav
"""

from __future__ import annotations

import os

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 44100
BPM = 100.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
BARS = 48
TOTAL = BARS * BAR + 0.8
N = int(TOTAL * SR)
rng = np.random.default_rng(7)

A = 440.0


def hz(midi: float) -> float:
    return A * 2 ** ((midi - 69) / 12)


def t_bar(bar: float) -> float:  # 1-based bar -> seconds
    return (bar - 1) * BAR


def lp(x, fc, order=2):
    return sosfilt(butter(order, min(fc, SR * 0.45) / (SR / 2), "low", output="sos"), x)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc / (SR / 2), "high", output="sos"), x)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo / (SR / 2), min(hi, SR * 0.45) / (SR / 2)], "band", output="sos"), x)


def env_adsr(n, a, d, s, r, sustain_len):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    sus = max(0, int(sustain_len * SR) - a - d)
    e = np.concatenate([np.linspace(0, 1, max(a, 1)), np.linspace(1, s, max(d, 1)), np.full(sus, s),
                        np.linspace(s, 0, max(r, 1))])
    return e[:n] if len(e) >= n else np.pad(e, (0, n - len(e)))


def saw(f, n, phase=0.0):
    t = np.arange(n) / SR
    return 2 * ((f * t + phase) % 1.0) - 1


def place(buf, sig, t0, gain=1.0):
    i = int(t0 * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += gain * sig[: j - i]


# ---------------------------------------------------------------- harmony
PROG = {  # chord tones (MIDI) per chord name
    "Am": [57, 60, 64], "F": [53, 57, 60], "C": [55, 60, 64], "G": [55, 59, 62],
    "Am9": [57, 60, 64, 71], "Fmaj7": [53, 57, 60, 64], "Esus": [52, 57, 59],
}
ROOT = {"Am": 45, "F": 41, "C": 48, "G": 43, "Am9": 45, "Fmaj7": 41, "Esus": 40}
LOOP = ["Am", "F", "C", "G"]


def chord_at(bar: int) -> str:
    if bar <= 6:
        return "Am"
    if bar <= 12:
        return ["Am", "Am", "F", "F", "Am", "Esus"][(bar - 7) % 6]
    if 29 <= bar <= 34:
        return ["Am", "Fmaj7", "Am", "Esus", "Am", "Am"][bar - 29]
    if bar >= 46:
        return ["F", "Esus", "Am9"][bar - 46]
    return LOOP[(bar - 1) % 4]


# ---------------------------------------------------------------- instruments
def pad_note(midi, dur, bright=1200):
    n = int((dur + 1.5) * SR)
    f = hz(midi)
    x = sum(saw(f * d, n, ph) for d, ph in ((1.0, 0), (1.004, .3), (0.996, .6))) / 3
    x = lp(x, bright)
    return x * env_adsr(n, 0.6, 0.4, 0.8, 1.4, dur)


def pluck(midi, dur=0.5, bright=3000):
    n = int((dur + 0.3) * SR)
    t = np.arange(n) / SR
    x = saw(hz(midi), n) * 0.6 + np.sign(np.sin(2 * np.pi * hz(midi) * t)) * 0.4
    x = lp(x, bright) * np.exp(-t * 7.0)
    return x


def bass_note(midi, dur, cutoff=500):
    n = int((dur + 0.1) * SR)
    t = np.arange(n) / SR
    x = saw(hz(midi), n) * 0.7 + np.sin(2 * np.pi * hz(midi) * t) * 0.6
    x = lp(x, cutoff + 1500 * np.exp(-t * 12).mean())
    return x * env_adsr(n, 0.005, 0.08, 0.7, 0.06, dur)


def kick(gain=1.0):
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * 7.5) + 0.25 * np.exp(-t * 90) * rng.standard_normal(n) * 0.3
    return gain * np.tanh(1.6 * x)


def snare(gain=1.0):
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    noise = bp(rng.standard_normal(n), 900, 7000) * np.exp(-t * 18)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)
    return gain * (0.8 * noise + 0.4 * tone)


def hat(gain=1.0, length=0.05):
    n = int(length * SR * 2)
    t = np.arange(n) / SR
    return gain * hp(rng.standard_normal(n), 7000) * np.exp(-t / length * 4)


def tick(gain=1.0):
    n = int(0.03 * SR)
    t = np.arange(n) / SR
    return gain * (np.sin(2 * np.pi * 2600 * t) * np.exp(-t * 300) + hp(rng.standard_normal(n), 4000) * np.exp(-t * 400) * 0.5)


def crash(gain=1.0):
    n = int(2.5 * SR)
    t = np.arange(n) / SR
    return gain * hp(rng.standard_normal(n), 4000) * np.exp(-t * 1.6)


def riser(dur, gain=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    steps = 24
    for k in range(steps):  # band sweeps upward
        a, b = k * n // steps, (k + 1) * n // steps
        lo = 300 * (2 ** (k / steps * 4))
        out[a:b] = bp(noise, lo, lo * 2.2)[a:b]
    sweep = np.sin(2 * np.pi * np.cumsum(200 + 1200 * (t / dur) ** 2) / SR) * 0.15
    return gain * (out + sweep) * (t / dur) ** 2


def boom(gain=1.0):
    n = int(3.0 * SR)
    t = np.arange(n) / SR
    f = 32 + 60 * np.exp(-t * 6)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.3)
    x += lp(rng.standard_normal(n), 900) * np.exp(-t * 4) * 0.6
    return gain * np.tanh(2.0 * x)


def stab_cluster(gain=1.0):
    # minor-second cluster, the "wrong" sound for the 46 ps failure
    n = int(2.0 * SR)
    t = np.arange(n) / SR
    x = sum(saw(hz(m), n) for m in (57, 58, 64, 65)) / 4
    return gain * lp(x, 1800) * np.exp(-t * 2.2)


def reverse_swell(dur, gain=1.0):
    return riser(dur, gain)[::-1][::-1] * 0 + gain * (lp(rng.standard_normal(int(dur * SR)), 3000) * np.linspace(0, 1, int(dur * SR)) ** 3)


# ---------------------------------------------------------------- arrangement
pads = np.zeros(N)
bass = np.zeros(N)
arp = np.zeros(N)
drums = np.zeros(N)
fx = np.zeros(N)

for bar in range(1, BARS + 1):
    t0 = t_bar(bar)
    ch = chord_at(bar)
    tones = PROG[ch]
    # pads: everywhere except a thinner intro
    if bar <= 6:
        if bar in (1, 4):
            for m in (45, 52, 57):  # drone A2 E3 A3
                place(pads, pad_note(m, 3 * BAR - 1.0, 700), t0, 0.22)
    elif not (bar == 33):
        bright = 900 if bar < 13 else 1400 if bar < 21 else 2200 if bar < 29 else 800 if bar < 35 else 1600
        if bar >= 46:
            bright = 1800
        for m in tones:
            place(pads, pad_note(m, BAR - 0.3, bright), t0, 0.16 if bar < 46 else 0.2)
    # sparse plucks in the intro
    if bar <= 12 and bar % 2 == 1:
        place(arp, pluck(76, 0.9, 2200), t0 + 2 * BEAT, 0.25)
        place(arp, pluck(72, 0.9, 2200), t0 + 3.5 * BEAT, 0.18)
    # bass
    groove = 21 <= bar <= 28 or 39 <= bar <= 45
    if 7 <= bar <= 32 or 35 <= bar <= 45:
        root = ROOT[ch]
        if bar <= 12 or 29 <= bar <= 32:
            for b in (0, 2):  # heartbeat half notes
                place(bass, bass_note(root, BEAT * 1.6, 300), t0 + b * BEAT, 0.5)
        else:
            for e in range(8):
                m = root + (12 if groove and e % 2 == 1 else 0)
                place(bass, bass_note(m, BEAT / 2 * 0.85, 700 if groove else 450), t0 + e * BEAT / 2, 0.42)
    # arpeggio (16ths) in build, groove and final
    if 13 <= bar <= 28 or 37 <= bar <= 45:
        if bar <= 20:
            bright = 700 + (bar - 13 + 1) / 8 * 3800
        elif bar <= 28:
            bright = 5000
        elif bar <= 38:
            bright = 900 + (bar - 37) * 1500
        else:
            bright = 5200
        pattern = [0, 1, 2, 1, 0, 2, 1, 2]
        for s in range(16):
            m = tones[pattern[s % 8] % len(tones)] + 12 + (12 if s % 8 == 7 else 0)
            place(arp, pluck(m, 0.22, bright), t0 + s * BEAT / 4, 0.16)
    # drums
    if 11 <= bar <= 12:
        place(drums, kick(0.6), t0)
        for b in range(4):
            place(drums, hat(0.12), t0 + b * BEAT + BEAT / 2)
    if 13 <= bar <= 20:
        kicks = (0, 2) if bar < 17 else (0, 1, 2, 3)
        for b in kicks:
            place(drums, kick(0.8), t0 + b * BEAT)
        if bar >= 15:
            for b in (1, 3):
                place(drums, snare(0.35), t0 + b * BEAT)
        for b in range(8):
            place(drums, hat(0.12 if b % 2 else 0.06), t0 + b * BEAT / 2)
        if bar == 20:  # roll + leave the last beat empty before the drop
            for k in range(12):
                place(drums, snare(0.15 + 0.35 * k / 12), t0 + 0 * BEAT + k * BEAT / 4)
            for k in range(8):
                place(drums, snare(0.45 + 0.2 * k / 8), t0 + 3 * BEAT + k * BEAT / 8 - BEAT * 0)
    if groove:
        for b in range(4):
            place(drums, kick(1.0), t0 + b * BEAT)
        for b in (1, 3):
            place(drums, snare(0.55), t0 + b * BEAT)
        for s in range(16):
            place(drums, hat(0.16 if s % 4 == 2 else 0.07), t0 + s * BEAT / 4)
        if bar in (21, 25, 39, 43):
            place(drums, crash(0.35), t0)
    if 35 <= bar <= 38:  # half-time rebuild
        place(drums, kick(0.85), t0)
        place(drums, kick(0.6), t0 + 2.5 * BEAT)
        place(drums, snare(0.5), t0 + 2 * BEAT)
        for b in range(8):
            place(drums, hat(0.09), t0 + b * BEAT / 2)
    # clock ticks: intro and tension
    if 4 <= bar <= 12 or 29 <= bar <= 34:
        g = 0.05 if bar <= 12 else 0.11
        for e in range(8):
            place(fx, tick(g * (1.3 if e % 2 == 0 else 0.8)), t0 + e * BEAT / 2)

# risers, impacts
place(fx, riser(2 * BAR, 0.5), t_bar(19))
place(fx, crash(0.5), t_bar(21))
place(fx, boom(0.9), t_bar(21))
place(fx, riser(BAR, 0.35), t_bar(32))
place(fx, boom(1.0), t_bar(33))
place(fx, stab_cluster(0.6), t_bar(33))
place(fx, crash(0.3), t_bar(33))
place(fx, riser(BAR, 0.35), t_bar(38))
place(fx, boom(0.7), t_bar(39))
place(fx, crash(0.25), t_bar(46))

# sidechain: duck pads and bass under kicks in the groove sections
duck = np.ones(N)
for bar in list(range(21, 29)) + list(range(39, 46)):
    for b in range(4):
        i = int((t_bar(bar) + b * BEAT) * SR)
        L = int(0.25 * SR)
        duck[i:i + L] = np.minimum(duck[i:i + L], 0.45 + 0.55 * np.linspace(0, 1, min(L, N - i)) ** 1.5)

# final fade over the last 1.6 s
fade = np.ones(N)
k = int(1.6 * SR)
fade[-k:] = np.linspace(1, 0, k) ** 1.5

mix_l = (pads * duck * 0.9 + bass * duck * 1.0 + arp * 0.85 + drums * 0.9 + fx * 0.9) * fade
mix_r = (pads * duck * 0.9 + bass * duck * 1.0 + np.roll(arp, int(0.011 * SR)) * 0.85 + drums * 0.9 + fx * 0.9) * fade
# light stereo width on pads
mix_l += np.roll(pads, int(0.007 * SR)) * 0.08 * fade
mix_r += np.roll(pads, int(0.013 * SR)) * 0.08 * fade

stereo = np.stack([mix_l, mix_r], axis=1)
stereo = hp(stereo.T, 28).T  # remove sub rumble
stereo = np.tanh(stereo * 1.4) / np.tanh(1.4)  # gentle saturation
peak = np.max(np.abs(stereo))
stereo = stereo / peak * 0.89  # about -1 dBFS
wavfile.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "score.wav"), SR, (stereo * 32767).astype(np.int16))
print(f"score.wav: {TOTAL:.1f} s, {BARS} bars at {BPM:.0f} BPM; drop at {t_bar(21):.1f} s, sting at {t_bar(33):.1f} s")
