import json
import math
import subprocess
import wave
from pathlib import Path
import numpy as np
from scipy.signal import butter, filtfilt

ROOT = Path(r"c:\Users\cross\Downloads\xc\creepy\ep02_nobody_leaves")
ASSETS = ROOT / "assets"
SAMPLES = Path(r"c:\Users\cross\Downloads\xc\SERIES_THEME\samples")
OUT_DIR = ROOT / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SR = 44100
DUR = 12.000
N = int(round(SR * DUR))


def read_wav_stereo(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as wf:
        ch, sw, sr = wf.getnchannels(), wf.getsampwidth(), wf.getframerate()
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
    arr = np.repeat(arr, 2, axis=1) if ch == 1 else arr[:, :2]
    if sr != SR:
        idx = np.linspace(0, len(arr) - 1, int(round(len(arr) * SR / sr)))
        arr = np.column_stack([np.interp(idx, np.arange(len(arr)), arr[:, c]) for c in range(2)]).astype(np.float32)
    return arr


def lowpass(arr: np.ndarray, cutoff_hz: float, order: int = 3) -> np.ndarray:
    b, a = butter(order, min(0.49, cutoff_hz / (SR * 0.5)), btype="low")
    return np.column_stack([filtfilt(b, a, arr[:, c]) for c in range(2)]).astype(np.float32)


def bandpass(arr: np.ndarray, lo_hz: float, hi_hz: float, order: int = 2) -> np.ndarray:
    b, a = butter(order, [max(0.001, lo_hz / (SR * 0.5)), min(0.49, hi_hz / (SR * 0.5))], btype="band")
    return np.column_stack([filtfilt(b, a, arr[:, c]) for c in range(2)]).astype(np.float32)


def add_at(mix: np.ndarray, clip: np.ndarray, start_sec: float, gain: float = 1.0, fade_in: float = 0.004, fade_out: float = 0.02):
    c = clip.copy()
    fi = min(len(c) // 2, int(fade_in * SR))
    fo = min(len(c) // 2, int(fade_out * SR))
    if fi > 0:
        c[:fi] *= np.linspace(0.0, 1.0, fi)[:, None]
    if fo > 0:
        c[-fo:] *= np.linspace(1.0, 0.0, fo)[:, None]
    s0 = int(round(start_sec * SR))
    if s0 >= N or s0 + len(c) <= 0:
        return
    c0 = max(0, -s0)
    m0 = max(0, s0)
    m1 = min(N, s0 + len(c))
    mix[m0:m1] += c[c0:c0 + (m1 - m0)] * gain


def synth_lofi_epiano() -> np.ndarray:
    """Warm detuned Rhodes chord progression with Beat 3 pitch-sag into dread."""
    # Fm9 -> DbMaj7 -> Eb6 -> C7b9 (3.0s per chord = 12.0s)
    chords = [
        (0.0, [174.61, 207.65, 261.63, 311.13, 392.00]),  # Fm9
        (3.0, [138.59, 207.65, 261.63, 329.63]),          # DbMaj7
        (6.0, [155.56, 233.08, 261.63, 311.13]),          # Eb6
        (8.4, [130.81, 196.00, 233.08, 277.18]),          # C7b9 (beat 3!)
    ]
    out = np.zeros((N, 2), dtype=np.float32)
    t_all = np.arange(N, dtype=np.float32) / SR
    # Smooth pitch droop starting at t=8.40s down to -1.5 semitones
    sag = np.where(t_all < 8.40, 1.0, 1.0 - 0.083 * np.clip((t_all - 8.40) / 1.4, 0.0, 1.0))

    for ci, (t0, freqs) in enumerate(chords):
        t1 = chords[ci + 1][0] if ci + 1 < len(chords) else DUR
        dur_c = min(DUR - t0, (t1 - t0) + 0.35)
        dn = int(dur_c * SR)
        tt = np.arange(dn, dtype=np.float32) / SR
        s0 = int(t0 * SR)
        s_seg = sag[s0:s0 + dn]
        sig = np.zeros((dn, 2), dtype=np.float32)
        for fi, f0 in enumerate(freqs):
            # Subtle wow/flutter + tine attack
            wobble = 1.0 + 0.0022 * np.sin(2.0 * math.pi * 0.85 * tt + fi)
            phase = np.cumsum((f0 * wobble * s_seg) * (2.0 * math.pi / SR))
            fund = np.sin(phase) * np.exp(-tt * 0.72)
            tine = 0.28 * np.sin(phase * 3.0) * np.exp(-tt * 5.2)
            tone = (fund + tine) * np.clip(tt / 0.015, 0.0, 1.0)
            pan = 0.35 + 0.3 * (fi / max(1, len(freqs) - 1))
            sig[:, 0] += tone * (1.0 - pan * 0.4)
            sig[:, 1] += tone * (0.6 + pan * 0.4)
        add_at(out, lowpass(sig, 2700.0), t0, gain=0.22, fade_in=0.01, fade_out=0.35)

    return out


def make_psx_blip(freq_hz: float, is_red: bool = False) -> np.ndarray:
    """Crisp 28ms low-pitched retro PS1 RPG dialogue blip."""
    dn = int(SR * 0.030)
    tt = np.arange(dn, dtype=np.float32) / SR
    # Hollow square/triangle wave quantized slightly like 8-bit SPU ADPCM
    sq = np.sign(np.sin(2.0 * np.pi * freq_hz * tt))
    tri = 2.0 * np.abs(2.0 * (tt * freq_hz - np.floor(tt * freq_hz + 0.5))) - 1.0
    raw = (0.45 * sq + 0.55 * tri) * np.exp(-tt * 95.0) * np.clip(tt / 0.002, 0.0, 1.0)
    # 5-bit coarse quantization grit + warm low-pass
    raw = np.round(raw * 16.0) / 16.0
    st = np.column_stack([raw, raw]).astype(np.float32)
    return lowpass(st, 1500.0 if is_red else 2400.0)


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

    # 1. Warm detuned lo-fi electric piano + Beat 3 dread tape pitch-sag
    mix += synth_lofi_epiano() * 0.72

    # 2. Real acoustic bass + trembling strings (Beat 3 seraph horror swell)
    bass_f = read_wav_stereo(SAMPLES / "bass_sus" / "BKCtbss_SusNV_D1_v3_rr1.wav")
    add_at(mix, lowpass(bass_f[:int(SR * 6.5)], 340.0), 0.0, gain=0.45, fade_in=0.5, fade_out=1.2)
    add_at(mix, lowpass(bass_f[:int(SR * 6.5)], 380.0), 6.0, gain=0.55, fade_in=0.8, fade_out=1.0)

    cello_trem = read_wav_stereo(SAMPLES / "cello_trem" / "trem_D2_v2_1.wav")
    vln_trem = read_wav_stereo(SAMPLES / "vln_trem" / "VlnEns_Trem_D5_v2.wav")
    add_at(mix, lowpass(cello_trem[:int(SR * 4.2)], 950.0), 7.80, gain=0.42, fade_in=0.65, fade_out=0.6)
    add_at(mix, bandpass(vln_trem[:int(SR * 3.8)], 420.0, 2100.0), 8.20, gain=0.22, fade_in=0.50, fade_out=0.7)

    # 3. Sample-accurate retro PS1 dialogue blips synced to typewriter_events.json
    events_path = ASSETS / "typewriter_events.json"
    if not events_path.exists():
        raise SystemExit(f"Missing {events_path} — run comp_psx.py first to export exact character timestamps!")
    events = json.loads(events_path.read_text(encoding="utf-8"))
    for idx_e, ev in enumerate(events):
        is_red = bool(ev["is_red"])
        f_hz = (158.0 + 18.0 * math.sin(idx_e * 0.7)) if is_red else (265.0 + 28.0 * math.sin(idx_e * 0.9))
        blip = make_psx_blip(f_hz, is_red=is_red)
        add_at(mix, blip, float(ev["time_sec"]), gain=0.28 if is_red else 0.22, fade_in=0.001, fade_out=0.004)

    # 4. Synced Diegetic Hallway SFX
    rng = np.random.default_rng(777)
    # 3.79s (f091): Faint electrical fluorescent light flicker buzz
    n_fl = int(SR * 0.26)
    t_fl = np.arange(n_fl, dtype=np.float32) / SR
    buzz = bandpass(rng.normal(0.0, 1.0, (n_fl, 2)).astype(np.float32), 850.0, 4200.0) * (0.4 + 0.6 * np.sin(2.0 * np.pi * 60.0 * t_fl))[:, None]
    add_at(mix, buzz, 3.76, gain=0.24, fade_in=0.01, fade_out=0.04)

    # 5.04s (f122): Metallic doorknob latch click + slow wooden door creak (5.1-7.2s)
    n_lk = int(SR * 0.045)
    t_lk = np.arange(n_lk, dtype=np.float32) / SR
    latch = bandpass(rng.normal(0.0, 1.0, (n_lk, 2)).astype(np.float32), 1400.0, 5200.0) * np.exp(-t_lk * 95.0)[:, None]
    add_at(mix, latch, 5.02, gain=0.45, fade_in=0.001, fade_out=0.01)

    n_cr = int(SR * 1.95)
    t_cr = np.arange(n_cr, dtype=np.float32) / SR
    cr_sig = np.sin(2.0 * np.pi * (160.0 - 38.0 * t_cr) * t_cr) * (0.5 + 0.5 * np.sin(2.0 * np.pi * (24.0 - 9.0 * t_cr) * t_cr))
    cr_nz = rng.normal(0.0, 0.35, (n_cr, 2)).astype(np.float32)
    creak = bandpass(cr_nz * 0.35 + cr_sig[:, None] * 0.65, 240.0, 980.0) * np.sin(np.pi * t_cr / 1.95)[:, None]
    add_at(mix, creak, 5.15, gain=0.20, fade_in=0.08, fade_out=0.25)

    # 8.42s (f203): Heavy wooden door SLAM + low-passed real timpani thud
    timp = read_wav_stereo(SAMPLES / "timp" / "Timpani1_Hit_v3_rr1_Sum.wav")
    add_at(mix, lowpass(timp[:int(SR * 1.5)], 260.0), 8.41, gain=0.68, fade_in=0.003, fade_out=0.5)
    n_sl = int(SR * 0.14)
    t_sl = np.arange(n_sl, dtype=np.float32) / SR
    slam_crack = lowpass(rng.normal(0.0, 1.0, (n_sl, 2)).astype(np.float32), 950.0) * np.exp(-t_sl * 32.0)[:, None]
    add_at(mix, slam_crack, 8.41, gain=0.50, fade_in=0.002, fade_out=0.03)

    # 5. Beat 3 Deep Sub-Heartbeat Pulse (8.45s-12.00s) + Leathery/Creaking Unfurl SFX (8.55s-10.2s)
    for beat_i in range(4):
        tb = 8.48 + beat_i * 0.88
        for off, f_hz, g_hb in ((0.0, 52.0, 0.58), (0.20, 46.0, 0.36)):
            dn_h = int(SR * 0.22)
            t_h = np.arange(dn_h, dtype=np.float32) / SR
            env_h = np.sin(np.pi * np.clip(t_h / 0.025, 0.0, 1.0)) * np.exp(-t_h * 14.0)
            sig_h = np.sin(2.0 * np.pi * (f_hz * (1.0 - 0.15 * t_h)) * t_h) * env_h
            add_at(mix, np.column_stack([sig_h, sig_h]).astype(np.float32), tb + off, gain=g_hb, fade_in=0.004, fade_out=0.02)

    n_un = int(SR * 1.65)
    t_un = np.arange(n_un, dtype=np.float32) / SR
    un_nz = bandpass(rng.normal(0.0, 1.0, (n_un, 2)).astype(np.float32), 180.0, 1150.0)
    un_cr = np.sin(2.0 * np.pi * (95.0 + 35.0 * t_un) * t_un) * np.sin(2.0 * np.pi * (14.0 - 4.0 * t_un) * t_un)
    unfurl = (un_nz * 0.55 + un_cr[:, None] * 0.45) * (np.sin(np.pi * t_un / 1.65) ** 0.8)[:, None]
    add_at(mix, lowpass(unfurl, 1200.0), 8.55, gain=0.22, fade_in=0.06, fade_out=0.25)

    # Subtle continuous dark corridor air hiss bed
    air = bandpass(rng.normal(0.0, 1.0, (N, 2)).astype(np.float32), 180.0, 820.0)
    mix += air * 0.025

    mix = np.tanh(mix * 2.2) * 0.72
    raw_wav = OUT_DIR / "ep02_audio_raw_v2.wav"
    master_wav = OUT_DIR / "ep02_audio_master_v2.wav"
    write_wav(raw_wav, mix)

    subprocess.run([
        "ffmpeg", "-y", "-i", str(raw_wav),
        "-af", "loudnorm=I=-13.8:TP=-2.8:LRA=4",
        "-ar", str(SR), "-ac", "2",
        str(master_wav),
    ], check=True)
    print(f"Mastered audio ({len(events)} synced PSX blips): {master_wav}")


if __name__ == "__main__":
    main()
