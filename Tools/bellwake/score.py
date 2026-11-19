"""Render six original looping chamber arrangements plus the bell cues, to mono Vorbis."""

from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile
import subprocess, tempfile, sys

dst = Path(__file__).resolve().parents[2] / "Assets/Resources/Bellwake/Audio"
rate = 22050


def voice(note, duration, kind):
    t = np.arange(round(duration * rate)) / rate
    freq = 440 * 2 ** ((note - 69) / 12)
    if kind == "reed":
        phase = 2 * np.pi * freq * t + 0.09 * np.sin(2 * np.pi * 4.8 * t)
        return (
            (0.82 * np.sin(phase) + 0.15 * np.sin(2 * phase) + 0.09 * np.sin(3 * phase))
            * np.minimum(1, t / 0.08)
            * np.minimum(1, (duration - t) / 0.18)
            * np.exp(-t * 0.38)
        )
    ratios, amps = {
        "bronze": ([1, 2.01, 2.71, 4.13], [0.69, 0.19, 0.15, 0.07]),
        "lute": ([1, 2, 3, 4], [0.7, 0.2, 0.13, 0.06]),
        "bass": ([1, 2, 3], [0.84, 0.12, 0.045]),
    }[kind]
    return (
        sum(
            a
            * np.sin(2 * np.pi * freq * r * t)
            * np.exp(-t * (1 + i * 0.62) * (2.1 if kind == "lute" else 1.35))
            for i, (r, a) in enumerate(zip(ratios, amps))
        )
        * np.minimum(1, t / 0.012)
        * np.minimum(1, (duration - t) / 0.12)
    )


def save(name, data):
    peak = max(abs(data))
    audio = (data / max(0.7, peak) * 26000).astype("int16")
    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        wavfile.write(f.name, rate, audio)
        subprocess.run(
            [
                "ffmpeg",
                "-loglevel",
                "error",
                "-y",
                "-i",
                f.name,
                "-c:a",
                "libvorbis",
                "-q:a",
                "3",
                str(dst / (name + ".ogg")),
            ],
            check=True,
        )


# Melodic contours and harmony change with the people inhabiting each place.
sets = [
    ("Bellmarket", 0.49, [62, 67, 65, 60], [7, 9, 12, None, 10, 7, None, 5, 4, None, 2, 0], "lute"),
    ("RootChoir", 0.57, [62, 58, 65, 60], [12, None, 7, 5, None, 3, 7, None, 5, 3, None, 0], "reed"),
    (
        "Reedwater",
        0.64,
        [57, 60, 53, 55],
        [7, None, None, 10, 9, None, 5, None, 2, None, 0, None],
        "reed",
    ),
    ("CinderLens", 0.44, [52, 55, 50, 52], [0, 7, None, 10, 7, 3, None, 5, 7, None, 2, None], "bronze"),
    (
        "StillBelfry",
        0.68,
        [50, 46, 48, 45],
        [12, None, None, 7, None, None, 3, None, 2, 0, None, None],
        "bronze",
    ),
    ("Morning", 0.55, [62, 67, 69, 62], [4, 7, 9, 12, None, 11, 7, 9, None, 4, 2, 0], "reed"),
    ("LowerWorks",.65,[50,55,57,52],[0,None,7,5,None,3,10,None,7,5,None,2],"bronze"),
    ("Waterworks",.56,[62,57,60,55],[5,7,None,10,9,None,5,2,None,3,2,0],"reed"),
    ("Bronzeworks",.47,[48,55,51,53],[0,7,3,None,12,10,None,7,3,None,2,0],"lute"),
    ("Lampworks",.71,[59,62,55,57],[12,None,7,9,None,5,2,None,3,7,None,0],"bronze"),
    ("Saltwake", .53,[59,62,64,57],[7,None,5,3,7,10,None,9,5,None,3,2],"lute"),
    ("RimePost", .72,[65,60,62,58],[12,None,None,7,8,None,5,3,None,5,None,0],"bronze"),
    ("Glasscut", .48,[54,57,52,59],[0,7,None,12,3,10,None,5,7,2,None,3],"reed"),
]
for idx, (name, beat, roots, line, instr) in enumerate(sets):
    if sys.argv[1:] and name not in sys.argv[1:]: continue
    # Preserve the original atmosphere seeds for existing witness-road districts.
    idx = {"Saltwake": 6, "RimePost": 7, "Glasscut": 8}.get(name, idx)
    n = round(48 * beat * rate)
    audio = np.zeros(n)

    def mix(at, sig, amp):
        pos = int(at * beat * rate) % n
        l = min(n - pos, len(sig))
        audio[pos : pos + l] += amp * sig[:l]
        if l < len(sig):
            audio[: len(sig) - l] += amp * sig[l:]

    for bar, base in enumerate(roots):
        for i, interval in enumerate(line):
            if interval is not None:
                sig = voice(base + interval, beat * (1.65 if instr == "reed" else 3.7), instr)
                mix(bar * 12 + i, sig, 0.30)
                mix(bar * 12 + i + 0.48, sig, 0.052)
        for i in (0, 4, 8):
            mix(bar * 12 + i, voice(base - 12, beat * 3.6, "bass"), 0.24)
            mix(bar * 12 + i + 2, voice(base + [7, 12, 5][i // 4], beat * 2.7, "lute"), 0.14)
    noise = np.random.default_rng(904 + idx).normal(0, 1, n)
    air = sosfilt(butter(2, [160, 1250], btype="bandpass", fs=rate, output="sos"), noise)
    audio += air * 0.023 * (0.65 + 0.35 * np.cos(np.arange(n) * 2 * np.pi / n))
    save(name, audio)
for name, note in [("Leaf", 67), ("Ember", 62), ("Tide", 57), ("Toll", 39)]:
    if sys.argv[1:] and name not in sys.argv[1:]: continue
    save(name, voice(note, 2.6, "bronze"))
