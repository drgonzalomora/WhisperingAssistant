from whispering_assistant.command_interface import BaseCommand

class Shutdown(BaseCommand):
    # Set the trigger for the 'Shutdown' command plugin
    trigger = "shutdown"

    def __init__(self, *args, **kwargs):
        pass

    def run(self, *args, **kwargs):
        # Your command execution logic here
        pass
