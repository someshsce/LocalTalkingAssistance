# LocalTalkingAssistance — Local Voice Assistant

> LocalTalkingAssistance is a simple, local voice assistant that runs on your computer. It listens, transcribes speech to text, processes the text, and speaks responses using local models — no cloud required.


![Screenshot](<example/Screenshot 2025-11-18 at 6.11.12 PM-1.png>)

## Output Audio

<audio controls src="example/output.wav" title="Title"></audio>

    <audio controls>
      <source src="example/output.wav" type="audio/wav">
      Your browser does not support the audio element.
    </audio>

## Key Features
- Multi-component voice pipeline: STT, TTS, trigger-word detection, and text processing.
- Uses local models where possible (Whisper, Silero VAD, Coqui/XTTS assets included).
- Designed to run on macOS/Linux with a Python virtual environment.

## Repository Layout

- `main.py` — Application entrypoint.
- `requirements.txt` — Python dependencies.
- `AI/` — Text processing helpers; includes `Text/ChatWithOllama.py`.
- `STT_Recognition/` — Speech-to-text and VAD; contains `silero`, `snowboy`, and `whisper` subfolders.
- `TTS_Synthesis/` — Text-to-speech helpers; includes `CoquiTTS.py` and `XTTS-v2` model files.

Some large model or runtime files are kept under subfolders (for example `whisper/models/base.pt` and `XTTS-v2/*`). If you need to replace or update these models, keep the same filenames/paths or update code references accordingly.

## Requirements

- Tested with Python 3.11 (other 3.x may work).
- Recommended: macOS or Linux with enough RAM/disk for model files.

Install system-level dependencies (macOS):

```bash
# Xcode command line tools (if not already installed)
xcode-select --install
```

## Setup (recommended: use virtualenv)

From the project folder run:

```bash
# create venv named 'voice_ai' (if you don't already have one)
python3 -m venv .voice_ai
# activate the venv (zsh)
source .voice_ai/bin/activate
# install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## Run

With your virtualenv activated, run the app:

```bash
python main.py
```

`main.py` is the top-level runner of the assistant. See `STT_Recognition/MainSpeechModule.py` for details on speech capture and pipeline orchestration.

## Components and Notes

- STT: `STT_Recognition/` contains modules for different recognition strategies. `whisper` contains model files (e.g., `base.pt`) — these are large and should be preserved.
- VAD: `STT_Recognition/silero` includes a precompiled `silero_vad` model.
- Wake-word: `STT_Recognition/snowboy` includes `svara.pmdl` (wake-word model) and resources.
- TTS: `TTS_Synthesis` includes `CoquiTTS.py` and an `XTTS-v2` folder with model checkpoints. These are large and may require GPU for best performance.

If you replace or move model files, update the corresponding module paths in the Python code.

## Models — downloading large files

The `XTTS-v2` model checkpoint (`model.pth`) is large and typically not committed to the repository. Below are two simple ways to fetch only that file from the Hugging Face `coqui/XTTS-v2` repo and place it into the expected folder `TTS_Synthesis/XTTS-v2/`.

Recommended (direct download, works if the file is public):

```bash
# create folder if needed (run from project root)
mkdir -p TTS_Synthesis/XTTS-v2

# download directly from Hugging Face (public file)
curl -L -o TTS_Synthesis/XTTS-v2/model.pth \
	https://huggingface.co/coqui/XTTS-v2/resolve/main/model.pth

# if the file requires authentication, set $HUGGINGFACE_TOKEN first and add the header:
# curl -L -H "Authorization: Bearer $HUGGINGFACE_TOKEN" -o TTS_Synthesis/XTTS-v2/model.pth \
#   https://huggingface.co/coqui/XTTS-v2/resolve/main/model.pth
```

Alternative (use `git-lfs` to fetch only the LFS object):

```bash
# clone the repo into a temporary folder, pull only the LFS object for model.pth,
# copy it into the project, then remove the temporary clone.
git clone https://huggingface.co/coqui/XTTS-v2 tmp_xtts
cd tmp_xtts
git lfs install --local
# fetch and checkout only the model.pth LFS object
git lfs pull --include "model.pth"
cp model.pth ../TTS_Synthesis/XTTS-v2/
cd ..
rm -rf tmp_xtts
```

Notes:
- The direct `curl` URL `https://huggingface.co/coqui/XTTS-v2/resolve/main/model.pth` works for public repos; if the repo requires authentication use an HF token as shown above.
- The `git lfs` approach requires `git-lfs` installed on your machine (`brew install git-lfs` on macOS) and may still download LFS objects — but the `--include` filter limits which LFS files are pulled.
- After placing `model.pth` in `TTS_Synthesis/XTTS-v2/`, your TTS code should find it at `TTS_Synthesis/XTTS-v2/model.pth`.

## Troubleshooting

- If Python fails with missing packages: ensure your virtualenv is activated and run `pip install -r requirements.txt`.
- If a model file is missing: verify the relevant file exists in `STT_Recognition/whisper/models/` or `TTS_Synthesis/XTTS-v2/`.
- Audio device issues: check macOS System Preferences → Sound, and ensure the app has microphone permissions.

## Contributing

1. Create an issue describing the change or bug.
2. Make a feature branch and open a PR with a clear title and description.

Please avoid committing huge binary model files — use LFS or provide external download instructions if you plan to change large models.

## License & Credits

This project is licensed under the Apache License 2.0 — see the `LICENSE` file for details. Also credit any third-party models and libraries used (Whisper, Silero, Coqui, Snowboy, etc.).

---
