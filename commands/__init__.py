# ...
# Check if the attribute is a subclass of BaseCommand and not the BaseCommand itself
if (
    isinstance(attribute, type)
    and issubclass(attribute, BaseCommand)
    and attribute is not BaseCommand
):
    # Register the command plugin in the COMMAND_PLUGINS dictionary
    command_trigger = attribute.trigger.lower()
    COMMAND_PLUGINS[command_trigger] = attribute

# Define the for loop function to run on all the commands