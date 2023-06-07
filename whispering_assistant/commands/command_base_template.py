from abc import ABC, abstractmethod
from functools import wraps

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


def requires_attributes(attrs):
    def decorator(cls):
        orig_init = cls.__init__

        @wraps(cls.__init__)
        def new_init(self, *args, **kwargs):
            for attr in attrs:
                if getattr(self, attr, None) is None:
                    raise NotImplementedError(f"Class {cls.__name__} must define the {attr} attribute.")
            orig_init(self, *args, **kwargs)

        cls.__init__ = new_init
        return cls

    return decorator


@requires_attributes(['trigger', 'command_type'])
class BaseCommand(ABC):
    """Base command interface for all command plugins."""

    # Define a class attribute for the trigger
    trigger = None  # string or "fallback"
    command_type = None  # command_types
    keywords = {
        "action": [""],
        "subject": [""]
    }

    def parameter_checker(self, raw_text, *args, **kwargs):
        pass

    @abstractmethod
    def run(self, text_parameter, raw_text, command_intent=None, *args, **kwargs):
        """Execute the desired action for the command plugin."""
        pass
