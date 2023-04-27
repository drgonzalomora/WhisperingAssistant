import subprocess
import time

from whispering_assistant.commands.command_base_template import BaseCommand, command_types


class MediaPlayBack(BaseCommand):
    trigger = "media_playback"
    command_type = command_types['ONE_SHOT']
    keywords = {
        "action": ["play", "pause", "next", "prev"],
        "subject": ["music", "video", "media"]
    }

    def run(self, text_parameter, raw_text, *args, **kwargs):
        raw_text = raw_text.lower()

        if 'prev' in raw_text:
            subprocess.run(["xdotool", "key", "XF86AudioPrev"])
            time.sleep(0.5)
            subprocess.run(["xdotool", "key", "XF86AudioPrev"])

        elif 'play' in raw_text or 'pause' in raw_text:
            subprocess.run(["xdotool", "key", "XF86AudioPlay"])

        elif 'skip' in raw_text or 'next' in raw_text:
            subprocess.run(["xdotool", "key", "XF86AudioNext"])

# MediaPlayBack().run(raw_text="play music", text_parameter=None)
