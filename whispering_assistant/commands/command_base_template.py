from abc import ABC, abstractmethod

command_types_names = [
    'ONE_SHOT',
    'CHAINABLE_LONG',
    'CHAINABLE_SHORT',
    'CHAINABLE_CONT'
]

# Initialize an empty dictionary to store the generated objects
command_types = {}

# Iterate over the command types array
for command_type in command_types_names:
    # Add the generated object to the dictionary
    command_types[command_type] = command_type

FALL_BACK_COMMAND = "FALL_BACK_COMMAND"


class BaseCommand(ABC):
    """Base command interface for all command plugins."""

    # Define a class attribute for the trigger
    trigger = None  # string or "fallback"
    command_type = None  # command_types
    keywords = {
        "action": [""],
        "subject": [""]
    }

    @abstractmethod
    def run(self, *args, **kwargs):
        """Execute the desired action for the command plugin."""
        pass
