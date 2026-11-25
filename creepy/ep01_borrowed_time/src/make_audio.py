import math
import subprocess
import wave
from pathlib import Path
import numpy as np
from scipy.signal import butter, filtfilt

ROOT = Path(r"c:\Users\cross\Downloads\xc\creepy\ep01_borrowed_time")
SAMPLES = Path(r"c:\Users\cross\Downloads\xc\SERIES_THEME\samples")
OUT_DIR = ROOT / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SR = 44100
DUR = 9.000
N = int(round(SR * DUR))


def read_wav_stereo(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as wf:
        ch = wf.getnchannels()
        sw = wf.getsampwidth()
        sr = wf.getframerate()
        raw = wf.readframes(wf.getnframes())
    if sw == 2:
        arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    elif sw == 3:
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        s = (b[:, 0].astype(np.int32) | (b[:, 1].astype(np.int32) << 8) | (b[:, 2].astype(np.int32) << 16))
        s = np.where(s >= 0x800000, s - 0x1000000, s)
        arr = s.astype(np.float32) / 8388608.0
    else:
        arr = np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2147483648.0

    arr = arr.reshape(-1, ch)
    if ch == 1:
        arr = np.repeat(arr, 2, axis=1)
    else:
        arr = arr[:, :2]
    if sr != SR:
        # Simple linear resample if needed
        idx = np.linspace(0, len(arr) - 1, int(round(len(arr) * SR / sr)))
        arr = np.column_stack([np.interp(idx, np.arange(len(arr)), arr[:, c]) for c in range(2)]).astype(np.float32)
    return arr


def pitch_shift_rate(arr: np.ndarray, cents: float) -> np.ndarray:
    ratio = 2.0 ** (cents / 1200.0)
    new_len = max(16, int(round(len(arr) / ratio)))
    idx = np.linspace(0, len(arr) - 1, new_len)
    return np.column_stack([np.interp(idx, np.arange(len(arr)), arr[:, c]) for c in range(2)]).astype(np.float32)


def add_wrap(mix: np.ndarray, clip: np.ndarray, start_sec: float, gain: float = 1.0, fade_in: float = 0.01, fade_out: float = 0.05):
    c = clip.copy()
    fi = min(len(c) // 2, int(fade_in * SR))
    fo = min(len(c) // 2, int(fade_out * SR))
    if fi > 0:
        c[:fi] *= np.linspace(0.0, 1.0, fi)[:, None]
    if fo > 0:
        c[-fo:] *= np.linspace(1.0, 0.0, fo)[:, None]
    s0 = int(round(start_sec * SR)) % N
    idx = (s0 + np.arange(len(c))) % N
    # Accumulate cleanly with modulo wrap so reverb tails wrap seamlessly around 9.000s loop!
    np.add.at(mix, idx, c * gain)


def lowpass(arr: np.ndarray, cutoff_hz: float, order: int = 3) -> np.ndarray:
    b, a = butter(order, min(0.49, cutoff_hz / (SR * 0.5)), btype="low")
    return np.column_stack([filtfilt(b, a, arr[:, c]) for c in range(2)]).astype(np.float32)


def bandpass(arr: np.ndarray, lo_hz: float, hi_hz: float, order: int = 2) -> np.ndarray:
    b, a = butter(order, [max(0.001, lo_hz / (SR * 0.5)), min(0.49, hi_hz / (SR * 0.5))], btype="band")
    return np.column_stack([filtfilt(b, a, arr[:, c]) for c in range(2)]).astype(np.float32)


def make_clock_tick(bright: float = 1.0, pitch_mult: float = 1.0) -> np.ndarray:
    """Crisp antique mechanical escapement tick (~45 ms)."""
    dur = 0.055
    n = int(SR * dur)
    t = np.arange(n, dtype=np.float32) / SR
    rng = np.random.default_rng(int(bright * 1000 + pitch_mult * 100))
    imp = rng.normal(0.0, 1.0, (n, 2)).astype(np.float32) * np.exp(-t * 140.0)[:, None]
    tone = (
        0.7 * np.sin(2.0 * np.pi * (1850.0 * pitch_mult) * t)
        + 0.4 * np.sin(2.0 * np.pi * (3420.0 * pitch_mult) * t)
    ).astype(np.float32) * np.exp(-t * 95.0)
    tick = bandpass(imp * 0.65 + tone[:, None] * 0.5, 900.0 * bright, 6500.0)
    return tick


def make_heartbeat(bpm_cycles: int = 8) -> np.ndarray:
    """8 seamless lub-dub sub-bass heartbeats over 9.000s (period = 1.125s)."""
    hb = np.zeros((N, 2), dtype=np.float32)
    period = DUR / bpm_cycles
    for i in range(bpm_cycles):
        t0 = i * period
        for offset, freq, amp in ((0.0, 56.0, 0.72), (0.21, 48.0, 0.44)):
            dn = int(SR * 0.24)
            tt = np.arange(dn, dtype=np.float32) / SR
            env = np.sin(np.pi * np.clip(tt / 0.03, 0, 1)) * np.exp(-tt * 14.0)
            sig = np.sin(2.0 * np.pi * (freq * (1.0 - 0.18 * tt)) * tt) * env
            pulse = np.column_stack([sig, sig]).astype(np.float32)
            add_wrap(hb, pulse, t0 + offset, gain=amp, fade_in=0.005, fade_out=0.02)
    return hb


def write_wav(path: Path, arr: np.ndarray):
    clipped = np.clip(arr, -0.99, 0.99)
    pcm = (clipped * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())


def main():
    mix = np.zeros((N, 2), dtype=np.float32)

    # 1. Deep acoustic D-minor sustained drone (real bass + cello)
    bass_d = read_wav_stereo(SAMPLES / "bass_sus" / "BKCtbss_SusNV_D1_v3_rr1.wav")
    cello_d = read_wav_stereo(SAMPLES / "cello_sus" / "susvib_D2_v3_1.wav")
    cello_a = read_wav_stereo(SAMPLES / "cello_sus" / "susvib_A2_v3_1.wav")

    add_wrap(mix, lowpass(bass_d[:int(SR * 5.5)], 360.0), 0.0, gain=0.60, fade_in=0.6, fade_out=1.2)
    add_wrap(mix, lowpass(bass_d[:int(SR * 5.5)], 360.0), 4.5, gain=0.60, fade_in=0.8, fade_out=1.2)
    add_wrap(mix, lowpass(cello_d[:int(SR * 5.5)], 750.0), 0.2, gain=0.35, fade_in=0.7, fade_out=1.1)
    add_wrap(mix, lowpass(cello_a[:int(SR * 5.0)], 650.0), 4.8, gain=0.30, fade_in=0.8, fade_out=1.1)

    # 2. Heartbeat pulse across entire 9.000s loop
    mix += make_heartbeat(bpm_cycles=8) * 0.50

    # 3. Eerie detuned music-box / harp / glockenspiel motif (minor 2nd tension)
    harp_d4 = pitch_shift_rate(read_wav_stereo(SAMPLES / "harp" / "KSHarp_D4_mf.wav"), -10.0)
    harp_f4 = pitch_shift_rate(read_wav_stereo(SAMPLES / "harp" / "KSHarp_F4_mf.wav"), -14.0)
    harp_e5 = pitch_shift_rate(read_wav_stereo(SAMPLES / "harp" / "KSHarp_E5_mf.wav"), -12.0)
    glock_c5 = pitch_shift_rate(read_wav_stereo(SAMPLES / "glock" / "glock_medium_C5.wav"), -18.0)

    add_wrap(mix, harp_d4[:int(SR * 2.5)], 0.15, gain=0.28, fade_in=0.005, fade_out=0.6)
    add_wrap(mix, harp_f4[:int(SR * 2.5)], 1.25, gain=0.24, fade_in=0.005, fade_out=0.6)
    add_wrap(mix, harp_e5[:int(SR * 2.5)], 3.40, gain=0.18, fade_in=0.005, fade_out=0.8)
    add_wrap(mix, glock_c5[:int(SR * 2.2)], 6.35, gain=0.20, fade_in=0.005, fade_out=0.7)

    # 4. Synced mechanical clock ticks matching build_scene.py keyframes!
    # 0.0-1.8s: crisp 1-second ticks at 0.0s, 1.0s
    tick_a = make_clock_tick(bright=1.0, pitch_mult=1.0)
    tick_b = make_clock_tick(bright=0.85, pitch_mult=0.92)
    add_wrap(mix, tick_a, 0.00, gain=0.55, fade_in=0.001, fade_out=0.01)
    add_wrap(mix, tick_b, 1.00, gain=0.52, fade_in=0.001, fade_out=0.01)

    # 1.8-4.8s (f044-f115): frantic counter-clockwise whirring ticks
    t_tick = 1.80
    i_t = 0
    while t_tick < 4.76:
        tk = make_clock_tick(bright=1.1, pitch_mult=0.88 + 0.05 * (i_t % 4))
        add_wrap(mix, tk, t_tick, gain=0.28 + 0.12 * ((t_tick - 1.8) / 3.0), fade_in=0.001, fade_out=0.008)
        t_tick += 0.115
        i_t += 1

    # 4.83s (f116): III:00 slam! Low timpani thud + brass/bell strike
    timp = read_wav_stereo(SAMPLES / "timp" / "Timpani1_Hit_v3_rr1_Sum.wav")
    gong = read_wav_stereo(SAMPLES / "perc" / "gongHit_f.wav")
    add_wrap(mix, lowpass(timp[:int(SR * 1.8)], 320.0), 4.82, gain=0.52, fade_in=0.004, fade_out=0.6)
    add_wrap(mix, lowpass(gong[:int(SR * 2.8)], 1200.0), 4.82, gain=0.16, fade_in=0.005, fade_out=1.0)

    # 5.4-7.8s: erratic stuttered ticks during tendril intrusion
    for st in (5.45, 5.72, 5.95, 6.32, 6.50, 6.88, 7.12, 7.45):
        add_wrap(mix, make_clock_tick(0.9, 0.84), st, gain=0.35, fade_in=0.001, fade_out=0.01)
    add_wrap(mix, tick_b, 8.00, gain=0.45, fade_in=0.001, fade_out=0.01)

    # 5. Intrusion 1 (1.85-4.9s): Subtle wooden doorframe creak + Cello tremolo swell
    rng_c = np.random.default_rng(2026)
    n_cr = int(SR * 0.72)
    t_cr = np.arange(n_cr, dtype=np.float32) / SR
    # Resonant woody squeak impulses slowing down like a tight hinge/jamb pressure
    creak_pulse = np.sin(2.0 * np.pi * (175.0 - 45.0 * t_cr) * t_cr) * (0.5 + 0.5 * np.sin(2.0 * np.pi * (28.0 - 12.0 * t_cr) * t_cr))
    creak_noise = rng_c.normal(0.0, 0.35, (n_cr, 2)).astype(np.float32)
    creak = bandpass(creak_noise * 0.4 + creak_pulse[:, None] * 0.6, 260.0, 920.0)
    creak *= np.sin(np.pi * t_cr / 0.72)[:, None]
    add_wrap(mix, creak, 1.85, gain=0.14, fade_in=0.05, fade_out=0.15)

    cello_trem = read_wav_stereo(SAMPLES / "cello_trem" / "trem_D2_v2_1.wav")
    add_wrap(mix, lowpass(cello_trem[:int(SR * 3.1)], 1100.0), 2.05, gain=0.34, fade_in=0.55, fade_out=0.7)

    # Cold draft air-gust whoosh right at III:00 slam (4.82s)
    n_g = int(SR * 0.95)
    t_g = np.arange(n_g, dtype=np.float32) / SR
    gust_sig = bandpass(rng_c.normal(0.0, 1.0, (n_g, 2)).astype(np.float32), 280.0, 1450.0)
    gust_sig *= (np.sin(np.pi * np.clip(t_g / 0.14, 0, 1)) * np.exp(-t_g * 3.2))[:, None]
    add_wrap(mix, gust_sig, 4.82, gain=0.22, fade_in=0.02, fade_out=0.20)

    # 6. Intrusion 2 (5.4-7.9s): Violin tremolo eerie harmonic tension + dark breathy air
    vln_trem = read_wav_stereo(SAMPLES / "vln_trem" / "VlnEns_Trem_D5_v2.wav")
    add_wrap(mix, bandpass(vln_trem[:int(SR * 2.6)], 550.0, 2600.0), 5.35, gain=0.22, fade_in=0.45, fade_out=0.75)

    # Filtered eerie air bed
    rng = np.random.default_rng(1234)
    air = bandpass(rng.normal(0.0, 1.0, (N, 2)).astype(np.float32), 240.0, 950.0)
    # Periodic swell envelope
    tt = np.arange(N, dtype=np.float32) / SR
    air_env = (0.018 + 0.012 * np.sin(2.0 * np.pi * tt / DUR))[:, None]
    mix += air * air_env

    # Soft analog saturation so crest factor matches -14.5 LUFS with TP <= -1.5 dBTP
    mix = np.tanh(mix * 2.4) * 0.72
    raw_wav = OUT_DIR / "ep01_audio_raw_v2.wav"
    master_wav = OUT_DIR / "ep01_audio_master_v2.wav"
    write_wav(raw_wav, mix)

    subprocess.run([
        "ffmpeg", "-y", "-i", str(raw_wav),
        "-af", "loudnorm=I=-13.8:TP=-2.8:LRA=4",
        "-ar", str(SR), "-ac", "2",
        str(master_wav),
    ], check=True)
    print("Wrote mastered audio:", master_wav)


if __name__ == "__main__":
    main()
