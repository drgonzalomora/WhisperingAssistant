from whispering_assistant.commands import execute_plugin_by_keyword
from whispering_assistant.commands.gpt_talk_with_clipboard_context import get_best_match

# use this to do some testing for plugin execution based on the transcript created.
# execute_plugin_by_keyword("send relation to ruby. use better prompts helper. I need to make an update to our existing application to add the new feature for calendar integration.")


# best_match = get_best_match(query="ruby, give me the shell command",
#                             items=[{'sample_command': ["give me the shell command"]}])
# print(best_match)
