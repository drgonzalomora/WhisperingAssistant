import threading
import time
import pyperclip as pyclip

# Try to force pyperclip to use a different clipboard backend:
pyclip.set_clipboard('xclip')


class ClipboardHandler:
    def __init__(self):
        self.clipboard_content = ""

    def load_clipboard(self, text_for_ingestion):
        self.clipboard_content = text_for_ingestion.lstrip()

    def restore_clipboard(self, old_clipboard):
        time.sleep(0.1)
        pyclip.copy(old_clipboard)

    def handle_clipboard(self, text_for_ingestion):
        old_clipboard = pyclip.paste().lstrip()
        if self.clipboard_content != text_for_ingestion:
            self.load_clipboard(text_for_ingestion)
        try:
            def copy_and_restore():
                time.sleep(3)
                pyclip.copy(self.clipboard_content)
                self.restore_clipboard(old_clipboard)

            clipboard_thread = threading.Thread(target=copy_and_restore)
            clipboard_thread.start()
        except Exception as e:
            print(f"An error occurred while handling the clipboard: {e}")


class TypingViaClipBoardHandler:
    def __init__(self):
        self.old_clipboard = ""

    def load_clipboard(self, text_parameter):
        try:
            self.old_clipboard = pyclip.paste()
            self.old_clipboard = self.old_clipboard.lstrip() if self.old_clipboard is not None else ""
        except Exception as e:
            self.old_clipboard = ""
            print(f"Error occurred while accessing clipboard: {e}")

        pyclip.copy(text_parameter.lstrip())

    def paste_input(self):
        print("Paste input")
        import pyautogui
        time.sleep(0.05)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.05)
        pyclip.copy(self.old_clipboard)

    def run_thread(self, text_parameter):
        def copy_paste_restore():
            self.load_clipboard(text_parameter)
            self.paste_input()

        clipboard_thread = threading.Thread(target=copy_paste_restore)
        clipboard_thread.start()


typingViaClipBoardHandler = TypingViaClipBoardHandler()
