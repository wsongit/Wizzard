"""The two field scores. Times inside a phrase are metrical beats, pitches are MIDI notes."""

import numpy as np
from scipy.signal import butter, sosfilt


def field_score(name, rate, voice):
    rook = name == "GlassPilots"
    beat = 0.36 if rook else 0.76
    meter = 6 if rook else 4
    # Durations and rests leave space for the search tool and the birds to answer.
    if rook:
        chords = [
            (50, 57, 64),
            (55, 59, 66),
            (52, 59, 67),
            (45, 55, 64),
            (50, 57, 66),
            (47, 54, 62),
            (43, 55, 64),
            (45, 57, 61),
            (55, 59, 66),
            (52, 55, 62),
            (50, 57, 66),
            (45, 57, 64),
            (47, 54, 62),
            (43, 55, 64),
            (45, 55, 61),
            (50, 57, 62),
        ]
        phrases = {
            0: [(1, 69, 0.9), (2.5, 74, 1.5), (4.5, 73, 0.8)],
            1: [(0, 71, 2.5), (3.5, 69, 1.2)],
            3: [(0, 67, 1), (1.5, 66, 1), (3, 64, 2.5)],
            5: [(1, 62, 1.4), (3, 69, 2.4)],
            6: [(0.5, 67, 1.2), (2, 71, 1.1), (4, 69, 1.5)],
            8: [(0, 74, 1), (1.5, 78, 1.1), (3, 76, 2.2)],
            9: [(1, 74, 1.5), (3, 71, 2.4)],
            11: [(0, 73, 1.8), (3, 69, 2.0)],
            12: [(0.5, 66, 1), (2, 69, 1), (3.5, 71, 2.2)],
            14: [(1, 67, 0.9), (2.5, 66, 1.2), (4.5, 64, 1)],
            15: [(0, 62, 3.5)],
        }
    else:
        chords = [
            (50, 57, 65),
            (46, 53, 62),
            (48, 55, 64),
            (45, 52, 62),
            (50, 57, 65),
            (53, 60, 64),
            (43, 55, 62),
            (45, 52, 61),
            (46, 53, 62),
            (48, 55, 64),
            (45, 57, 61),
            (50, 57, 62),
        ]
        phrases = {
            0: [(0.5, 65, 0.8), (1.6, 67, 0.75), (2.75, 69, 1.1)],
            1: [(0, 65, 2.3)],
            2: [(1, 64, 0.8), (2, 62, 1.6)],
            4: [(0.5, 57, 0.9), (1.8, 62, 1), (3, 65, 0.8)],
            5: [(0, 69, 1.6), (2, 67, 0.9), (3, 64, 0.85)],
            6: [(1, 62, 2.4)],
            8: [(0, 65, 1.3), (2, 69, 1.5)],
            9: [(0.5, 67, 1.1), (2, 64, 1.5)],
            11: [(0, 62, 2.9)],
        }
    length = round(len(chords) * meter * beat * rate)
    audio = np.zeros(length)

    def put(start, samples, gain):
        i = round(start * beat * rate) % length
        n = min(len(samples), length - i)
        audio[i : i + n] += samples[:n] * gain
        if n < len(samples):
            audio[: len(samples) - n] += samples[n:] * gain

    def air_note(midi, beats):
        t = np.arange(round(beats * beat * rate)) / rate
        hz = 440 * 2 ** ((midi - 69) / 12)
        phase = 2 * np.pi * hz * t + 0.18 * np.sin(2 * np.pi * 4.2 * t) * np.minimum(1, t / 0.45)
        line = (
            np.sin(phase)
            + (0.09 if rook else 0.22) * np.sin(2 * phase + 0.13)
            + 0.052 * np.sin(3 * phase)
        )
        return (
            line
            * np.minimum(1, t / 0.08)
            * np.minimum(1, (len(t) / rate - t) / 0.14)
            * (0.84 + 0.16 * np.cos(t * 2.0))
        )

    for bar, (low, fifth, top) in enumerate(chords):
        start = bar * meter
        put(start, voice(low - 12, beat * (3.6 if rook else 3.2), "bass"), 0.18)
        if rook:
            for at, note in [(0, fifth), (2, top), (3.5, fifth + 12)]:
                put(start + at, voice(note, beat * 2.8, "lute"), 0.125 if at == 0 else 0.085)
            if bar in (2, 7, 10, 13):
                put(start + 4.5, voice(top + 12, beat * 4.5, "bronze"), 0.055)
        else:
            put(start + 0.12, voice(fifth, beat * 2.5, "lute"), 0.095)
            put(start + 2.35, voice(top, beat * 2.8, "lute"), 0.085)
            if bar in (3, 7, 10):
                put(start + 3.1, voice(fifth - 5, beat * 0.8, "bass"), 0.10)
        for at, note, span in phrases.get(bar, []):
            melody = air_note(note, span)
            put(start + at, melody, 0.20 if rook else 0.16)
            put(start + at + 0.42, melody, 0.025)
    breath = np.random.default_rng(541 if rook else 294).normal(size=length)
    band = [480, 1450] if rook else [180, 630]
    air = sosfilt(butter(2, band, btype="bandpass", fs=rate, output="sos"), breath)
    audio += air * 0.008 * (0.6 + 0.4 * np.sin(np.arange(length) * 2 * np.pi / length))
    return audio


def silver_bath(rate, voice):
    """A waltz for bottle glass, a bowed reed and the press rack. Fold tails across the loop."""
    beat = 0.92
    chords = [(48,55,62), (44,55,63), (46,53,62), (43,53,59),
              (48,55,63), (51,58,65), (46,53,60), (43,55,62),
              (41,53,60), (44,55,63), (43,53,59), (48,55,62)]
    tune = [(0,.5,67,1.4),(1,0,68,1.5),(1,2,63,.8),(2,0,65,1.8),
            (3,1,62,1.4),(4,0,63,2.3),(5,.5,70,1.5),(6,0,68,.8),
            (6,1,65,1.8),(7,1,62,1.8),(8,0,60,1.8),(9,1,63,1.8),
            (10,.5,59,1.2),(11,0,60,2.2)]
    length = round(beat * 3 * len(chords) * rate)
    mix = np.zeros(length)

    def add(at, sound, gain):
        start = round(at * beat * rate) % length
        n = min(length - start, len(sound))
        mix[start:start+n] += gain * sound[:n]
        if n < len(sound):
            mix[:len(sound)-n] += gain * sound[n:]

    for bar, (root, fifth, colour) in enumerate(chords):
        start = bar * 3
        add(start, voice(root-12, 2.15, "bass"), .32)
        add(start+.5, voice(fifth, 1.42, "lute"), .20)
        add(start+1.5, voice(colour, 1.45, "bronze"), .13)
        if bar % 4 == 2:
            add(start+2.5, voice(fifth+12, 1.75, "bronze"), .085)
    for bar, at, midi, beats in tune:
        phrase = voice(midi, beats*beat, "reed")
        add(3*bar+at, phrase, .27)
        add(3*bar+at+.38, phrase, .055)
    return mix
