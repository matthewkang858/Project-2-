#!/usr/bin/env bash
# Recreate the narrator's environment on a fresh machine: a Python venv with the voice and the recogniser, and the
# model files, so that  $TTS tools/narrate.py <film>  can speak a film's narration again.
#
#     bash tools/setup_tts.sh            # from the project root
#
#   MC_TTS_ENV      where the venv goes        (default: the session scratchpad, .../scratchpad/tts)
#   MC_TTS_MODELS   where the model files go   (default: .../scratchpad/tts_models; tools/narrate.py reads the same variable)
#   PYTHON          the interpreter to build the venv from (default python3; made and tested with CPython 3.13)
#
# It is a SEPARATE environment from Blender's (bpy cannot share an interpreter with these packages): films are built
# with $BPY, the narration is spoken with $TTS = $MC_TTS_ENV/bin/python, and the two only meet in narration/*.wav|json.
# Needs: ffmpeg on PATH (resampling, loudness measurement), about 1.2 GB of disk, network access to PyPI,
# github.com (model release files) and huggingface.co (the recogniser).
#
# What is installed (the versions the committed narrations were made with; Kokoro and the recogniser are
# deterministic on CPU, so the same versions reproduce narration/*.wav bit for bit on the machine they were made on):
#   kokoro-onnx 0.6.1    Kokoro 82M text to speech (Apache-2.0) through onnxruntime 1.32.0, espeak-ng phonemes
#   faster-whisper 1.2.1 the recogniser (model small.en, MIT), ctranslate2 4.9.1
#   soundfile 0.14.0     wav writing;   numpy 2.5.5
#   onnx 1.23.2          used ONCE by `narrate.py --make-timed-model` (exposes the model's phoneme durations)
# Model files:
#   kokoro-v1.0.onnx   310 MB  sha256 7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5
#   voices-v1.0.bin     27 MB  sha256 bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d
#       https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/
#   Systran/faster-whisper-small.en (revision d1d751a5...) from the Hugging Face hub, fetched by faster-whisper itself
#   kokoro-v1.0.timed.onnx     made locally from kokoro-v1.0.onnx (same weights, one more output; sha256
#       4d7ae8ccd19c712c9353e358110c66d3a075e0a962303f0d6ad6a69258816c94 with onnx 1.23.2). tools/narrate.py does
#       not speak a film without it (exit code 1), unless --recogniser-only is given: remake it with
#       `$TTS tools/narrate.py --make-timed-model` if the models directory was cleared.
set -euo pipefail

SCRATCH="/tmp/claude-0/-home-user-Project-2-/be90bb9d-3fc7-572c-941a-ff79c8b6ef48/scratchpad"
TTS_ENV="${MC_TTS_ENV:-$SCRATCH/tts}"
MODELS="${MC_TTS_MODELS:-$SCRATCH/tts_models}"
PY="${PYTHON:-python3}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RELEASE="https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"

command -v ffmpeg >/dev/null || { echo "ffmpeg is not on PATH: install it first"; exit 1; }

if [ ! -x "$TTS_ENV/bin/python" ]; then
    "$PY" -m venv "$TTS_ENV"
fi
"$TTS_ENV/bin/python" -m pip install --quiet --upgrade pip
"$TTS_ENV/bin/python" -m pip install --quiet \
    "kokoro-onnx==0.6.1" "faster-whisper==1.2.1" "soundfile==0.14.0" "onnxruntime==1.32.0" "ctranslate2==4.9.1" \
    "numpy==2.5.5" "onnx==1.23.2"

mkdir -p "$MODELS"
fetch() {   # name, sha256
    if [ -f "$MODELS/$1" ] && echo "$2  $MODELS/$1" | sha256sum --check --status; then
        echo "have $1"
        return
    fi
    curl --location --fail --retry 3 --output "$MODELS/$1.part" "$RELEASE/$1"
    echo "$2  $MODELS/$1.part" | sha256sum --check --status || { echo "checksum of $1 is wrong"; exit 1; }
    mv "$MODELS/$1.part" "$MODELS/$1"
    echo "fetched $1"
}
fetch kokoro-v1.0.onnx 7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5
fetch voices-v1.0.bin bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d

# the recogniser: faster-whisper downloads Systran/faster-whisper-small.en into $MODELS (its own cache layout)
MC_TTS_MODELS="$MODELS" "$TTS_ENV/bin/python" - <<'EOF'
import os
from faster_whisper import WhisperModel
WhisperModel("small.en", device="cpu", compute_type="int8", download_root=os.environ["MC_TTS_MODELS"])
print("have the recogniser model small.en")
EOF

# the voice model with its phoneme durations exposed (checks that the audio is bit-identical to the original's)
if [ ! -f "$MODELS/kokoro-v1.0.timed.onnx" ]; then
    MC_TTS_MODELS="$MODELS" "$TTS_ENV/bin/python" "$ROOT/tools/narrate.py" --make-timed-model
fi

echo
echo "ready:  export TTS=$TTS_ENV/bin/python  MC_TTS_MODELS=$MODELS"
echo "        \$TTS tools/narrate.py <film>          # speak films/<film>.py's NARRATION into narration/"
echo "        \$TTS tools/narrate.py --selftest      # timing accuracy (run until it prints the report)"
