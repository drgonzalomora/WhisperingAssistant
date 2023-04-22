from whispering_assistant.commands.command_base_template import BaseCommand, FALL_BACK_COMMAND
import pyperclip
import time
import subprocess

x2, y2, width2, height2 = 630, 900, 1600, 1200
region2 = (x2, y2, width2, height2)
image2 = '/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/images/CHAT_BOX.png'

def paste_input():
    import pyautogui

    curr_clipboard = pyperclip.paste()
    # Look for image2 on the screen
    image2_location = pyautogui.locateOnScreen(image2, region=region2, confidence=0.8)

    if image2_location is not None:
        print(f"Image 2 found at {image2_location}")

        # Click on the center of image2
        image2_center = pyautogui.center(image2_location)
        pyautogui.click(image2_center)

        # Type the string
        pyautogui.typewrite(curr_clipboard)
        time.sleep(0.5)

        # Press the enter key
        pyautogui.press('enter')
        print("Typing and pressing enter done.")
    else:
        print("Image 2 not found on the screen.")
        # Simulate pressing Ctrl+V

        pyautogui.hotkey('ctrl', 'v')

        # Get the active window's name
        active_window_name = get_active_window_name()

        print(active_window_name)

        # Check if the active window's name contains "Google Chrome" or "Atom"
        if "Atom" in active_window_name:
            # Simulate pressing the Return key
            pyautogui.press('enter')


def get_active_window_name():
    cmd = "xdotool getactivewindow getwindowname"
    window_name = subprocess.check_output(cmd, shell=True).decode().strip()
    return window_name


class TypeInput(BaseCommand):
    trigger = FALL_BACK_COMMAND

    def run(self, *args, text_parameter="", **kwargs):
        old_clipboard = pyperclip.paste()
        pyperclip.copy(text_parameter)
        time.sleep(0.5)
        paste_input()
        pyperclip.copy(old_clipboard)
        action_done = "clipboard_type_input"
        return action_done
