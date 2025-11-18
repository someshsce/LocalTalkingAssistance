import time
import logging
from STT_Recognition import MainSpeechModule as sr
from AI.Text import ChatWithOllama as chat
from TTS_Synthesis.CoquiTTS import TTSHandler
from rich.markdown import Markdown
from rich.console import Console

logging.getLogger().setLevel(logging.ERROR)

tts = TTSHandler()
console = Console()

YINFO = f"\n[bold yellow]INFO[/bold yellow]"
BINFO = f"\n[bold blue]INFO[/bold blue]"
ERROR = f"\n[bold red]ERROR[/bold red]"
USER = f"\n[bold cyan]USER[/bold cyan]"
LANG = f"[bold cyan]LANG[/bold cyan]"
AI = f"\n[bold purple]AI[/bold purple]"
SYS = f"\n[bold magenta]SYSTEM[/bold magenta]"

def MainLoop():
    """
    Main loop function to handle continuous interaction.
    """
    with sr.Microphone() as source: 
        sr.Recognizer().adjust_for_ambient_noise(source)

        while True:
            console.print(f"{BINFO} Listening for Human Call....")
            
            if sr.Recognizer().human_call(source):
                console.print(f"{BINFO} Human Call detected, start listening for command...")
                last_interaction_time = time.time()
                system_active = True

                while system_active:
                    if time.time() - last_interaction_time > 900:
                        console.print(f"{YINFO} No interaction detected for a long time. Returning to wake word detection.")
                        system_active = False
                        break
                    
                    with console.status(f"\n[bold green]Listening...[/bold green]") as status:
                        audio = sr.Recognizer().listen(source)

                        if audio:
                            if sr.Recognizer().voice_activity_detection(audio):
                                console.print(f"{BINFO} Voice Activity detected")

                                if tts.tts_thread and tts.tts_thread.is_alive():
                                    tts.pause()
                                    tts.tts_thread.join()
                                    console.print(f"{YINFO} TTS wait(paused) in another thread due to new voice activity.")
                                
                                status.update(f"\n[bold green]Processing your speech to text...[/bold green]")
                                last_interaction_time = time.time()
                                data = sr.Recognizer().recognize_whisper(audio)
                            
                                query = data['text']
                                lang = data['language']
                                
                                if query:
                                    console.print(f"{USER}{query}")
                                    console.print(f"{LANG} {lang}")
                                    
                                    normalized_text = ' '.join(word.strip('.').lower() for word in query.strip().split())
                                    
                                    if any(cmd in normalized_text for cmd in ["stop", "keep quiet", "quiet", "stop speaking"]):
                                        console.print(f"{SYS} Stopping...")
                                        tts.stop()
                                        continue

                                    elif any(cmd in normalized_text for cmd in ["pause", "hold on"]):
                                        console.print(f"{SYS} Pausing...")
                                        tts.pause()
                                        continue

                                    elif any(cmd in normalized_text for cmd in ["resume", "continue"]):
                                        console.print(f"{SYS} Resuming...")
                                        tts.unpause()
                                        continue
                                    
                                    status.update(f"\n[bold green]Processing your query...[/bold green]")
                                    msg = chat.TextAI(query)
                                    if msg:
                                        console.print(f"{AI} ", Markdown(msg), end="")
                                        status.stop()
                                        tts.speak_in_thread(msg)
                                    else:
                                        console.print(f"{YINFO} Failed to generate response.")
                                else:
                                    console.print(f"{YINFO} STT conversion resulted in empty text.")
                        else:
                            console.print(f"{YINFO} Failed to capture audio.")
                        
                        time.sleep(0.1)

if __name__ == "__main__":
    try:
        MainLoop()
    except KeyboardInterrupt:
        console.print(f"{BINFO} Program interrupted by user.")
