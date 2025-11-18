import os
import torch
from TTS.api import TTS
import contextlib
import io
from rich.console import Console
import threading

with contextlib.redirect_stdout(io.StringIO()):
    import pygame

console = Console()

BINFO = f"\n[bold blue]INFO[/bold blue]"
ERROR = f"\n[bold red]ERROR[/bold red]"

class TTSHandler:
    def __init__(self):
        try:
            pygame.mixer.init()
            self._pygame_ready = True
        except Exception:
            console.print(f"{ERROR} Failed to initialize pygame mixer. Audio playback disabled.")
            self._pygame_ready = False
        self.tts_thread = None
        self.tts_stop_event = threading.Event()
        self.audio_file_path = None

    def generate_tts(self, text):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        model_path = os.path.join("TTS_Synthesis", "XTTS-v2")
        config_path = os.path.join("TTS_Synthesis", "XTTS-v2", "config.json")
        output_path = os.path.join("TTS_Synthesis", "output.wav")
        
        try:
            console.print(f"{BINFO} Speech Synthesizer is Synthesizing the AI response...")
            with contextlib.redirect_stdout(io.StringIO()):
                tts = TTS(model_path=model_path, config_path=config_path, vocoder_path=None, vocoder_config_path=None, progress_bar=False, gpu=(device == "cuda")).to(device)
                tts.tts_to_file(text=text, speaker_wav="TTS_Synthesis/XTTS-v2/samples/hindiFem.wav", language="en", file_path=output_path)

            # Success
            self.audio_file_path = output_path
            console.print(f"{BINFO} Synthesis is completed!")
            console.print(f"{BINFO} TTS is playing the response from another thread (You can Interrupt by speaking)...")
            return output_path

        except KeyboardInterrupt:
            console.print(f"{ERROR} Synthesis interrupted by user.")
            return None

        except Exception as e:
            console.print(f"{ERROR} Error during Synthesizing: {e}")
            return None

    def play_audio(self, file_path):
        if not file_path:
            console.print(f"{ERROR} No audio file to play (synthesis likely failed).")
            return

        if not os.path.isfile(file_path):
            console.print(f"{ERROR} Audio file not found: {file_path}")
            return

        if not getattr(self, "_pygame_ready", False):
            console.print(f"{ERROR} Pygame mixer not initialized; cannot play audio.")
            return

        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                if self.tts_stop_event.is_set():
                    pygame.mixer.music.stop()
                    break
        except Exception as e:
            console.print(f"{ERROR} Playback error: {e}")
            return

    def play(self, text):
        output_path = self.generate_tts(text)
        if not output_path:
            # Synthesis failed or was interrupted; nothing to play.
            return
        self.play_audio(output_path)

    def speak_in_thread(self, msg):
        self.tts_stop_event.clear()
        self.tts_thread = threading.Thread(target=self.play, args=(msg,))
        self.tts_thread.start()

    def stop(self):
        self.tts_stop_event.set()
        pygame.mixer.music.stop()

    def pause(self):
        pygame.mixer.music.pause()

    def unpause(self):
        pygame.mixer.music.unpause()
