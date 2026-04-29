"""
synthesizer.py
==============
A monophonic, additive synthesizer that converts a melody (given as MIDI note
numbers) into audio.  The user is guided through every step via prompts, and
the result can be played through the sound-card and/or saved to a .wav file.

Modules used (all encountered in class):
    numpy, sounddevice, soundfile

Bonus features implemented:
    * Rests  - any negative MIDI number inserts a silent beat.
    * Per-note durations  - the user may optionally supply a list of beat
      multipliers (1.0 = one beat, 0.5 = half a beat, 2.0 = two beats, …).
    * Timbre presets  - 1 = sawtooth, 2 = square, 3 = triangle.
    * Effects  - optional delay (echo) and/or soft-clipping distortion.
    * Synthesizer class  - all DSP logic is encapsulated in a class.

Author : Logan Silvers
Course : Art of Code
Date   : 4/29/2026
"""

# ---------------------------------------------------------------------------
# Standard / third-party imports
# ---------------------------------------------------------------------------
import sys
import numpy as np
import sounddevice as sd
import soundfile as sf

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SAMPLE_RATE: int = 44100          # samples per second (CD quality)
MIDI_MIN: int = 0                 # lowest legal MIDI note
MIDI_MAX: int = 127               # highest legal MIDI note
BPM_MIN: float = 10.0             # minimum sensible tempo (BPM)
BPM_MAX: float = 400.0            # maximum sensible tempo (BPM)
A4_MIDI: int = 69                 # MIDI number for concert A (440 Hz)
A4_FREQ: float = 440.0            # frequency of concert A (Hz)
ATTACK_FRAC: float = 0.10         # fraction of note duration used for attack
DECAY_FRAC: float = 0.15          # fraction of note duration used for decay
N_HARMONICS: int = 40             # maximum number of harmonic overtones


# ===========================================================================
# Synthesizer class
# ===========================================================================
class Synthesizer:
    """
    A monophonic, additive synthesizer.

    Parameters
    ----------
    sample_rate : int
        Audio sample rate in samples per second (default 44 100 Hz).
    timbre : int
        Waveform preset:
            1 = sawtooth (default)
            2 = square
            3 = triangle
    use_delay : bool
        When True a simple tape-echo effect is applied to the final mix.
    use_distortion : bool
        When True soft-clipping distortion is applied to the final mix.
    """

    # -----------------------------------------------------------------------
    # Construction
    # -----------------------------------------------------------------------
    def __init__(
        self,
        sample_rate: int = SAMPLE_RATE,
        timbre: int = 1,
        use_delay: bool = False,
        use_distortion: bool = False,
    ) -> None:
        self.sample_rate = sample_rate
        self.timbre = timbre
        self.use_delay = use_delay
        self.use_distortion = use_distortion

    # -----------------------------------------------------------------------
    # Static / pure conversion helpers
    # -----------------------------------------------------------------------
    @staticmethod
    def midi2freq(midi_note: int) -> float:
        """
        Convert a MIDI note number to its frequency in Hz.

        Uses the standard equal-temperament formula:
            f = 440 * 2^((n - 69) / 12)

        Parameters
        ----------
        midi_note : int
            MIDI note number in the range [0, 127].

        Returns
        -------
        float
            Frequency in Hz.

        Examples
        --------
        >>> Synthesizer.midi2freq(69)
        440.0
        >>> round(Synthesizer.midi2freq(60), 2)
        261.63
        """
        return A4_FREQ * (2.0 ** ((midi_note - A4_MIDI) / 12.0))

    @staticmethod
    def bpm2sec(bpm: float) -> float:
        """
        Convert a tempo in BPM to the duration of one beat in seconds.

        Parameters
        ----------
        bpm : float
            Tempo in beats per minute.

        Returns
        -------
        float
            Duration of one beat in seconds.

        Examples
        --------
        >>> Synthesizer.bpm2sec(60.0)
        1.0
        >>> Synthesizer.bpm2sec(120.0)
        0.5
        """
        return 60.0 / bpm

    def sec2samples(self, duration_sec: float) -> int:
        """
        Convert a duration in seconds to the equivalent number of samples.

        Parameters
        ----------
        duration_sec : float
            Duration in seconds.

        Returns
        -------
        int
            Number of audio samples (always at least 1).
        """
        return max(1, int(round(duration_sec * self.sample_rate)))

    # -----------------------------------------------------------------------
    # Oscillator
    # -----------------------------------------------------------------------
    def oscillator(self, freq: float, n_samples: int) -> np.ndarray:
        """
        Generate one period-accurate additive waveform.

        The waveform type is chosen by ``self.timbre``:

        * **Sawtooth** (timbre=1) – all harmonics, amplitude ∝ 1/k
        * **Square**   (timbre=2) – odd harmonics only, amplitude ∝ 1/k
        * **Triangle** (timbre=3) – odd harmonics only, amplitude ∝ 1/k²,
          alternating sign

        Band-limiting: harmonics whose frequency would exceed the Nyquist
        limit (sample_rate / 2) are silently omitted, preventing aliasing.

        Parameters
        ----------
        freq : float
            Fundamental frequency in Hz.
        n_samples : int
            Number of samples to generate.

        Returns
        -------
        np.ndarray
            Normalised (peak ≤ 1.0) mono audio array of length *n_samples*.
        """
        t = np.linspace(0.0, n_samples / self.sample_rate, n_samples, endpoint=False)
        signal = np.zeros(n_samples, dtype=np.float64)
        nyquist = self.sample_rate / 2.0

        for k in range(1, N_HARMONICS + 1):
            harmonic_freq = freq * k

            # Band-limit: skip harmonics beyond Nyquist
            if harmonic_freq >= nyquist:
                break

            # --- Sawtooth: all harmonics, amplitude = 1/k ---
            if self.timbre == 1:
                signal += (1.0 / k) * np.sin(2.0 * np.pi * harmonic_freq * t)

            # --- Square: odd harmonics, amplitude = 1/k ---
            elif self.timbre == 2:
                if k % 2 == 1:
                    signal += (1.0 / k) * np.sin(2.0 * np.pi * harmonic_freq * t)

            # --- Triangle: odd harmonics, amplitude = 1/k², alternating phase ---
            elif self.timbre == 3:
                if k % 2 == 1:
                    sign = (-1.0) ** ((k - 1) // 2)
                    signal += sign * (1.0 / k ** 2) * np.sin(2.0 * np.pi * harmonic_freq * t)

        # Normalise to prevent clipping
        peak = np.max(np.abs(signal))
        if peak > 0.0:
            signal /= peak

        return signal

    # -----------------------------------------------------------------------
    # Envelope
    # -----------------------------------------------------------------------
    def envelope(self, n_samples: int) -> np.ndarray:
        """
        Create a simple linear attack–decay (AD) amplitude envelope.

        The envelope has:
          * An *attack* phase that ramps from 0 → 1 over the first
            ``ATTACK_FRAC`` fraction of the note.
          * A *decay* phase that ramps from 1 → 0 over the last
            ``DECAY_FRAC`` fraction of the note.
          * A *sustain* plateau at amplitude 1 in between.

        Parameters
        ----------
        n_samples : int
            Total length of the note in samples.

        Returns
        -------
        np.ndarray
            Envelope array of length *n_samples* with values in [0, 1].
        """
        env = np.ones(n_samples, dtype=np.float64)

        attack_samples = int(ATTACK_FRAC * n_samples)
        decay_samples = int(DECAY_FRAC * n_samples)

        # Attack ramp: 0 → 1
        if attack_samples > 0:
            env[:attack_samples] = np.linspace(0.0, 1.0, attack_samples)

        # Decay ramp: 1 → 0
        if decay_samples > 0:
            env[-decay_samples:] = np.linspace(1.0, 0.0, decay_samples)

        return env

    # -----------------------------------------------------------------------
    # Single note
    # -----------------------------------------------------------------------
    def note(self, midi_note: int, duration_sec: float) -> np.ndarray:
        """
        Synthesize a single note or rest.

        A **rest** is requested by passing a negative *midi_note* value; it
        returns a block of silence with the correct duration.

        Parameters
        ----------
        midi_note : int
            MIDI note number (0–127) for a pitched note, or any negative
            integer for a silent rest.
        duration_sec : float
            Desired duration in seconds.

        Returns
        -------
        np.ndarray
            Mono audio array for this note/rest.
        """
        n_samples = self.sec2samples(duration_sec)

        # Rest
        if midi_note < 0:
            return np.zeros(n_samples, dtype=np.float64)

        # Pitched note = oscillator × envelope
        freq = self.midi2freq(midi_note)
        wave = self.oscillator(freq, n_samples)
        env = self.envelope(n_samples)
        return wave * env

    # -----------------------------------------------------------------------
    # Full melody
    # -----------------------------------------------------------------------
    def melody(
        self,
        note_list: list,
        bpm: float,
        durations: list = None,
    ) -> np.ndarray:
        """
        Synthesize an entire melody by concatenating individual notes.

        Parameters
        ----------
        note_list : list of int
            MIDI note numbers.  Negative values are treated as rests.
        bpm : float
            Tempo in beats per minute.  Each beat = one note (unless
            *durations* is supplied).
        durations : list of float, optional
            Beat multipliers for each note, e.g. ``[1.0, 0.5, 1.5, …]``.
            A value of ``1.0`` means one beat; ``2.0`` means two beats, etc.
            Must have the same length as *note_list* if provided.

        Returns
        -------
        np.ndarray
            Full mono audio signal for the melody, normalised to peak ≤ 0.9.
        """
        beat_sec = self.bpm2sec(bpm)

        if durations is None:
            durations = [1.0] * len(note_list)

        audio_chunks = []
        for midi_note, dur_mult in zip(note_list, durations):
            duration_sec = beat_sec * dur_mult
            chunk = self.note(midi_note, duration_sec)
            audio_chunks.append(chunk)

        full_audio = np.concatenate(audio_chunks)

        # Normalise whole melody to 90 % of full scale
        peak = np.max(np.abs(full_audio))
        if peak > 0.0:
            full_audio = 0.9 * full_audio / peak

        return full_audio

    # -----------------------------------------------------------------------
    # Effects
    # -----------------------------------------------------------------------
    def apply_delay(
        self,
        audio: np.ndarray,
        delay_sec: float = 0.35,
        feedback: float = 0.45,
        mix: float = 0.40,
    ) -> np.ndarray:
        """
        Apply a simple tape-echo (feedback delay) effect.

        Parameters
        ----------
        audio : np.ndarray
            Input mono audio signal.
        delay_sec : float
            Echo delay time in seconds (default 0.35 s).
        feedback : float
            Fraction of the echo signal fed back into itself (0–1).
        mix : float
            Wet/dry mix: 0.0 = fully dry, 1.0 = fully wet (default 0.4).

        Returns
        -------
        np.ndarray
            Processed audio with the same length as *audio*.
        """
        delay_samples = self.sec2samples(delay_sec)
        wet = np.zeros(len(audio) + delay_samples, dtype=np.float64)
        wet[: len(audio)] = audio

        # Iteratively add decaying echoes
        n_echoes = int(np.log(0.01) / np.log(max(feedback, 1e-9)))
        for i in range(1, max(n_echoes, 1) + 1):
            start = i * delay_samples
            amp = feedback ** i
            if start >= len(wet):
                break
            end = min(start + len(audio), len(wet))
            wet[start:end] += amp * audio[: end - start]

        # Trim back to original length
        wet = wet[: len(audio)]

        # Normalise then mix
        peak = np.max(np.abs(wet))
        if peak > 0.0:
            wet /= peak

        return (1.0 - mix) * audio + mix * wet

    @staticmethod
    def apply_distortion(audio: np.ndarray, drive: float = 5.0) -> np.ndarray:
        """
        Apply soft-clipping distortion via a hyperbolic-tangent shaper.

        Parameters
        ----------
        audio : np.ndarray
            Input mono audio signal.
        drive : float
            Amount of pre-gain before the clipper (> 1 = more distortion).

        Returns
        -------
        np.ndarray
            Distorted audio, normalised to peak ≤ 0.9.
        """
        distorted = np.tanh(drive * audio)
        peak = np.max(np.abs(distorted))
        if peak > 0.0:
            distorted = 0.9 * distorted / peak
        return distorted

    # -----------------------------------------------------------------------
    # High-level render
    # -----------------------------------------------------------------------
    def render(
        self,
        note_list: list,
        bpm: float,
        durations: list = None,
    ) -> np.ndarray:
        """
        Render a melody to a NumPy array, applying any enabled effects.

        Parameters
        ----------
        note_list : list of int
            MIDI note numbers (negatives = rests).
        bpm : float
            Tempo in beats per minute.
        durations : list of float, optional
            Per-note beat multipliers.

        Returns
        -------
        np.ndarray
            Final processed audio as a float64 array.
        """
        audio = self.melody(note_list, bpm, durations)

        if self.use_distortion:
            print("  Applying distortion …")
            audio = self.apply_distortion(audio)

        if self.use_delay:
            print("  Applying delay (echo) …")
            audio = self.apply_delay(audio)

        return audio


# ===========================================================================
# Input helpers
# ===========================================================================

def get_note_list() -> list:
    """
    Prompt the user for a comma-separated list of MIDI note numbers.

    Validates that every entry is an integer; negatives are accepted as rests.
    Entries outside [MIDI_MIN, MIDI_MAX] are clamped with a warning.

    Returns
    -------
    list of int
        Validated list of MIDI note numbers / rest markers.
    """
    while True:
        raw = input(
            "\nInput the melody as a comma-separated list of MIDI note values\n"
            f"  (integers {MIDI_MIN}–{MIDI_MAX}; any negative number = rest):\n  > "
        ).strip()

        if not raw:
            print("  ✗  No input detected. Please try again.")
            continue

        try:
            notes = list(map(int, raw.split(",")))
        except ValueError:
            print("  ✗  Could not parse input. Make sure every value is an integer.")
            continue

        if len(notes) == 0:
            print("  ✗  The list is empty. Please enter at least one note.")
            continue

        # Validate / clamp pitched notes
        validated = []
        for n in notes:
            if n < 0:
                # Treat as rest – no clamping needed
                validated.append(n)
            elif n < MIDI_MIN:
                print(f"  ⚠  {n} is below {MIDI_MIN} – clamped to {MIDI_MIN}.")
                validated.append(MIDI_MIN)
            elif n > MIDI_MAX:
                print(f"  ⚠  {n} exceeds {MIDI_MAX} – clamped to {MIDI_MAX}.")
                validated.append(MIDI_MAX)
            else:
                validated.append(n)

        print(f"  ✓  Accepted {len(validated)} note(s) / rest(s).")
        return validated


def get_bpm() -> float:
    """
    Prompt the user for a tempo in BPM.

    Accepts any float between BPM_MIN and BPM_MAX.

    Returns
    -------
    float
        Validated tempo in beats per minute.
    """
    while True:
        raw = input(
            f"\nInput the tempo in BPM (beats per minute) [{BPM_MIN}–{BPM_MAX}]:\n  > "
        ).strip()
        try:
            bpm = float(raw)
        except ValueError:
            print("  ✗  Please enter a numeric value.")
            continue

        if bpm < BPM_MIN:
            print(f"  ⚠  {bpm} BPM is very slow; clamped to minimum {BPM_MIN} BPM.")
            bpm = BPM_MIN
        elif bpm > BPM_MAX:
            print(f"  ⚠  {bpm} BPM is very fast; clamped to maximum {BPM_MAX} BPM.")
            bpm = BPM_MAX

        print(f"  ✓  Tempo set to {bpm} BPM.")
        return bpm


def get_durations(n_notes: int) -> list:
    """
    Optionally prompt the user for per-note beat multipliers.

    The user may skip this step (press Enter) to use uniform durations of 1.0.

    Parameters
    ----------
    n_notes : int
        Number of notes in the melody (used for validation).

    Returns
    -------
    list of float or None
        List of beat multipliers, or None for uniform durations.
    """
    print(
        f"\nOptionally, input {n_notes} comma-separated beat-duration multipliers\n"
        "  (1.0 = one beat, 0.5 = half a beat, 2.0 = two beats, etc.).\n"
        "  Press Enter to skip and use uniform 1-beat durations."
    )
    raw = input("  > ").strip()

    if not raw:
        print("  ✓  Using uniform 1-beat durations.")
        return None

    try:
        durs = list(map(float, raw.split(",")))
    except ValueError:
        print("  ✗  Could not parse durations – using uniform 1-beat durations.")
        return None

    if len(durs) != n_notes:
        print(
            f"  ✗  Expected {n_notes} values but got {len(durs)} – "
            "using uniform 1-beat durations."
        )
        return None

    if any(d <= 0.0 for d in durs):
        print("  ✗  All durations must be positive – using uniform 1-beat durations.")
        return None

    print(f"  ✓  Custom durations accepted.")
    return durs


def get_timbre() -> int:
    """
    Prompt the user to choose a timbre preset.

    Returns
    -------
    int
        1 = sawtooth, 2 = square, 3 = triangle.
    """
    print(
        "\nChoose a timbre preset by entering its number:\n"
        "  1 – Sawtooth  (bright, buzzy)\n"
        "  2 – Square    (hollow, reedy)\n"
        "  3 – Triangle  (soft, flute-like)\n"
        "  Press Enter to use the default (1 – Sawtooth)."
    )
    raw = input("  > ").strip()

    if raw == "":
        print("  ✓  Using default: Sawtooth.")
        return 1

    try:
        choice = int(raw)
    except ValueError:
        print("  ✗  Invalid input – using default: Sawtooth.")
        return 1

    if choice not in (1, 2, 3):
        print("  ✗  Choice must be 1, 2, or 3 – using default: Sawtooth.")
        return 1

    names = {1: "Sawtooth", 2: "Square", 3: "Triangle"}
    print(f"  ✓  Timbre set to: {names[choice]}.")
    return choice


def get_effects() -> tuple:
    """
    Ask the user whether to apply delay and/or distortion.

    Returns
    -------
    (bool, bool)
        (use_delay, use_distortion)
    """
    def yes_no(prompt: str) -> bool:
        while True:
            ans = input(prompt + " [yes/no]: ").strip().lower()
            if ans in ("yes", "y"):
                return True
            if ans in ("no", "n"):
                return False
            print("  ✗  Please enter 'yes' or 'no'.")

    print("\n--- Effects ---")
    use_delay = yes_no("  Apply delay (echo) effect?")
    use_distortion = yes_no("  Apply soft-clipping distortion?")
    return use_delay, use_distortion


def get_yes_no(prompt: str) -> bool:
    """
    Generic yes/no prompt.

    Parameters
    ----------
    prompt : str
        Question to display to the user.

    Returns
    -------
    bool
        True if the user answered yes, False otherwise.
    """
    while True:
        ans = input(prompt + " [yes/no]: ").strip().lower()
        if ans in ("yes", "y"):
            return True
        if ans in ("no", "n"):
            return False
        print("  ✗  Please enter 'yes' or 'no'.")


def get_filename() -> str:
    """
    Prompt the user for an output filename.

    Ensures the returned name ends with '.wav'.

    Returns
    -------
    str
        Output filename.
    """
    raw = input("\nEnter the output filename (e.g. melody.wav):\n  > ").strip()
    if not raw:
        raw = "output.wav"
    if not raw.lower().endswith(".wav"):
        raw += ".wav"
    return raw


# ===========================================================================
# Playback and file I/O
# ===========================================================================

def play_audio(audio: np.ndarray, sample_rate: int) -> None:
    """
    Play a NumPy audio array through the default sound card.

    Parameters
    ----------
    audio : np.ndarray
        Mono float64 audio signal.
    sample_rate : int
        Sample rate in Hz.
    """
    if sd is None:
        print("  ✗  sounddevice is not installed – cannot play audio.")
        return

    print("  ▶  Playback started …")
    try:
        sd.play(audio.astype(np.float32), samplerate=sample_rate)
        sd.wait()
        print("  ■  Playback finished successfully.")
    except Exception as exc:
        print(f"  ✗  Playback failed: {exc}")


def save_wav(audio: np.ndarray, sample_rate: int, filename: str) -> None:
    """
    Write a NumPy audio array to a .wav file.

    Parameters
    ----------
    audio : np.ndarray
        Mono float64 audio signal.
    sample_rate : int
        Sample rate in Hz.
    filename : str
        Output path (should end with '.wav').
    """
    if sf is None:
        print("  ✗  soundfile is not installed – cannot save .wav file.")
        return

    print(f"  💾  Writing to '{filename}' …")
    try:
        sf.write(filename, audio.astype(np.float32), sample_rate, subtype="PCM_16")
        print(f"  ✓  File saved successfully: '{filename}'")
    except Exception as exc:
        print(f"  ✗  File write failed: {exc}")


# ===========================================================================
# Main entry point
# ===========================================================================

def main() -> None:
    """
    Main interactive loop.

    Guides the user through:
      1. Melody input (MIDI note numbers)
      2. Tempo input (BPM)
      3. Optional per-note durations
      4. Timbre preset selection
      5. Optional effects
      6. Synthesis
      7. Optional playback
      8. Optional .wav export
    """
    print("=" * 60)
    print("  Monophonic Additive Synthesizer")
    print("=" * 60)

    # --- Step 1: Melody ---
    note_list = get_note_list()

    # --- Step 2: Tempo ---
    bpm = get_bpm()

    # --- Step 3: Durations (bonus) ---
    durations = get_durations(len(note_list))

    # --- Step 4: Timbre (bonus) ---
    timbre = get_timbre()

    # --- Step 5: Effects (bonus) ---
    use_delay, use_distortion = get_effects()

    # --- Step 6: Synthesis ---
    print("\n--- Synthesizing melody …")
    synth = Synthesizer(
        sample_rate=SAMPLE_RATE,
        timbre=timbre,
        use_delay=use_delay,
        use_distortion=use_distortion,
    )
    audio = synth.render(note_list, bpm, durations)
    duration_sec = len(audio) / SAMPLE_RATE
    print(f"  ✓  Done. Total duration: {duration_sec:.2f} s  |  {len(audio)} samples.")

    # --- Step 7: Playback ---
    print()
    if get_yes_no("Play the melody now?"):
        play_audio(audio, SAMPLE_RATE)

    # --- Step 8: Save to .wav ---
    print()
    if get_yes_no("Save the melody to a .wav file?"):
        filename = get_filename()
        save_wav(audio, SAMPLE_RATE, filename)

    print("\nGoodbye!\n")


# ---------------------------------------------------------------------------
# Guard
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Interrupted by user. Exiting.")
        sys.exit(0)