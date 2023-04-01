from abc import ABC, abstractmethod

class BaseCommand(ABC):
    """Base command interface for all command plugins."""

    # Define a class attribute for the trigger
    trigger = None
    keywords = {
        "action": [""],
        "subject": [""]
    }

    @abstractmethod
    def __init__(self, *args, **kwargs):
        """Constructor for the command plugin."""
        pass

    @abstractmethod
    def run(self, *args, **kwargs):
        """Execute the desired action for the command plugin."""
        pass
