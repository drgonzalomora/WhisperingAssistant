from whispering_assistant.commands.command_base_template import BaseCommand, FALL_BACK_COMMAND
import time

from whispering_assistant.utils.clipboard_manager import TypingViaClipBoardHandler
from whispering_assistant.utils.window_dialogs import get_active_window_name

x2, y2, width2, height2 = 0, 540, 1920, 1080
region2 = (x2, y2, width2, height2)
image2 = '/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/images/CHAT_BOX.png'


class GptTypingViaClipBoardHandler(TypingViaClipBoardHandler):
    def paste_input(self):
        active_window_name = get_active_window_name()
        print("active_window_name", active_window_name)

        if 'google chrome' in active_window_name.lower():
            import pyautogui

            # Look for image2 on the screen
            image2_location = pyautogui.locateOnScreen(image2, region=region2, confidence=0.8)

            if image2_location is not None:
                print(f"Image 2 chat box found at {image2_location}")

                # Click on the center of image2
                image2_center = pyautogui.center(image2_location)
                pyautogui.click(image2_center)

                # Type the string
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.1)

                # Press the enter key
                pyautogui.press('enter')
                print("Typing and pressing enter done.")
            else:
                print("Image 2 chat box not found on the screen.")
                # Simulate pressing Ctrl+V

                pyautogui.hotkey('ctrl', 'v')
        else:
            print("Image 2 chat box not found on the screen.")
            # Simulate pressing Ctrl+V
            import pyautogui
            pyautogui.hotkey('ctrl', 'v')


gptTypingViaClipBoardHandler = GptTypingViaClipBoardHandler()


class TypeInput(BaseCommand):
    trigger = FALL_BACK_COMMAND

    def run(self, *args, text_parameter="", **kwargs):
        gptTypingViaClipBoardHandler.run_thread(text_parameter.lstrip())
        action_done = "clipboard_type_input"
        return action_done
