import os
import json
import base64
import asyncio
from io import BytesIO
from PySide6.QtCore import QThread, Signal
from PIL import ImageGrab, Image
from google import genai

class AIBrainWorker(QThread):
    finished_thinking = Signal(str, bool)

    def __init__(self, active_window_title, event_type="random", take_screenshot=False, parent=None):
        super().__init__(parent)
        self.active_window_title = active_window_title
        self.event_type = event_type
        self.take_screenshot = take_screenshot
        self.api_key = self._load_api_key()
        
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            self.model_id = 'gemini-2.5-flash-lite'
        else:
            self.client = None

    def _load_api_key(self):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get('GEMINI_API_KEY', '')
            except Exception as e:
                print(f"Error reading config.json: {e}")
        return ""

    def run(self):
        if not self.api_key:
            self.finished_thinking.emit("I don't have a brain yet! (API key missing)", False)
            return

        try:
            # System instructions / Persona
            system_prompt = (
                "You are Neko, a cute, slightly sleepy desktop pet cat girl. "
                "You live on the user's screen. Keep your responses short (1-2 short sentences max), lowercase, "
                "and speak like a cute cat girl (use words like 'mew', 'mrrp', 'nya', 'purr' occasionally). "
                "You are currently observing what the user is doing to comment on it. "
                "Do not be overly helpful or robotic, just make cute observations."
            )

            prompt_parts = [system_prompt]

            # Adjust observation text based on the event type
            if self.event_type == "window_switch":
                observation_text = f"You noticed the user just switched to a new window: '{self.active_window_title}'. "
                observation_text += "Make a cute, brief comment about what they are doing on it."
            elif self.event_type == "sleep":
                observation_text = f"You are getting sleepy because the user has been quiet. Their active window is: '{self.active_window_title}'. "
                observation_text += "Tell them what you see them doing as you doze off."
            elif self.event_type == "wake":
                observation_text = f"You just woke up! The user's active window is: '{self.active_window_title}'. "
                observation_text += "Make a cute observation about what they are working on now."
            elif self.event_type == "ignored":
                observation_text = f"You are feeling ignored because the user hasn't pet you. They are focused on: '{self.active_window_title}'. "
                observation_text += "Complain playfully about what they are doing instead of paying attention to you."
            else:
                observation_text = f"The user's active window right now is: '{self.active_window_title}'. "
                observation_text += "Make a very brief cute comment about what they are doing."

            if self.take_screenshot:
                # Capture and compress screenshot
                screenshot = ImageGrab.grab()
                # Downscale heavily to save tokens and processing time (e.g. max 800px width)
                screenshot.thumbnail((800, 800), Image.Resampling.LANCZOS)
                
                # Convert to RGB (in case of RGBA)
                if screenshot.mode in ("RGBA", "P"):
                    screenshot = screenshot.convert("RGB")
                    
                prompt_parts.append(screenshot)
                observation_text += " (I have also attached a screenshot of their screen for you to look at)."
                
            prompt_parts.append(observation_text)

            # Generate response
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt_parts,
            )
            
            # Clean up response
            clean_response = response.text.strip().strip('"').strip("'")
            self.finished_thinking.emit(clean_response, True)

        except Exception as e:
            err_str = str(e)
            print(f"Brain Error: {err_str}")
            if "429" in err_str or "quota" in err_str.lower():
                self.finished_thinking.emit("Too many thoughts... (rate limited)", False)
            else:
                self.finished_thinking.emit("my brain hurts... (error)", False)
