import whispering_assistant.commands
from whispering_assistant.utils.command_intent_detection import generate_index_for_intent_detection
from whispering_assistant.utils.gpt_prompt_injections import generate_index_prompt_for_injection

# 📌 TODO: Add a logic to delete all the indexes and hash databases before regenerating all the indexes and cache
generate_index_for_intent_detection()

# 📌 TODO: Copy the file deletion logic from the intent detection index function. So that we should clear the indexes first before we generate a new one.
# Think of a way on how to put this as a utility function so we can use it for future index generation functions.
generate_index_prompt_for_injection()