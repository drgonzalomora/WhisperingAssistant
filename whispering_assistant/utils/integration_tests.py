# ⚠️ use this to do some testing for plugin execution based on the transcript created.

# v 🚥🚥🚥
# import inflect

# def num_to_words(s):
#     p = inflect.engine()
#     words = s.split()
#     new_words = []
#     for word in words:
#         if word.replace('.', '').isdigit():  # Check if the word is a number
#             if '.' in word:  # Handle decimal number
#                 whole, decimal = word.split('.')
#                 whole_word = p.number_to_words(whole)
#                 decimal_word = ' '.join([p.number_to_words(i) for i in decimal])
#                 new_words.append(f"{whole_word} point {decimal_word}")
#             else:  # Handle whole number
#                 new_words.append(p.number_to_words(word))
#         elif word.isupper() and len(word) > 1:  # Check if the word is an abbreviation
#             new_words.append('...'.join(list(word)) + '...')
#         else:
#             new_words.append(word)
#     return ' '.join(new_words)
#
# s = "i have 2.1 change in my AMD shares"
# print(num_to_words(s))  # "i have two point one change in my A...M...D... shares"
#

# v 🚥🚥🚥
# from whispering_assistant.utils.tts_test import tts_queue
#
#
# def emptypass():
#     pass
#
#
# tts_queue.put(("with revenue .A.G.I.", emptypass))

# v 🚥🚥🚥
# import re
#
# multiline_string = """
# 🗣️ Action: SEARCH
#
# Action Input: "Philippines current weather"
# """
#
# match = re.search(r'Action Input: ?"?(.*?)"?$', multiline_string, re.MULTILINE)
# if match:
#     action_input = match.group(1).strip()  # Use strip() to remove leading/trailing whitespaces
#     print(f'Action Input: {action_input}')
# else:
#     print('No match found.')

# 🚥🚥🚥
# 📌 Test difflib threshold
# from whispering_assistant.commands.gpt_talk_with_clipboard_context import get_best_match
# best_match = get_best_match(query="use the following tool for asking nora generating a summarized progress reports from a given context. example command: create a detailed progress report",
#                             items=[{'desc': "use the following tool for asking {assistant_name} generating a summarized progress reports from a given context. example command: create a detailed progress report"}])
# print(best_match)

# 🚥🚥🚥
# 📌 Test intent analysis logic per plugin
from whispering_assistant.commands import execute_plugin_by_keyword

# result_text = "send context to nora. Can you convert the following date time in PHT time zone?"
# result_text = "nora. Can you convert the following date time in PHT time zone?"
# result_text = "nora. can you summarize the time logs?"
# result_text = "can you summarize the time logs?"
# result_text = "added the keyword shutdown for better accuracy of the analysis"
# result_text = "shutdown"
# result_text = "send relation to nora. update the following python code to use print instead"
# result_text = "nora, create a python code that shows the prime number with a given input"
# result_text = 'search google for the current time in PHT'
# result_text = "lock screen 11"
# execute_plugin_by_keyword(result_text, skip_fallback=True, run_command=False)

# 🚥🚥🚥
# 📌 Test parsing of the command desc
# from whispering_assistant.commands import execute_plugin
# from whispering_assistant.utils.command_intent_detection import parse_plugin_commands_examples
#
# intent_list = parse_plugin_commands_examples()
#
# print("intent_list", intent_list)

# 🚥🚥🚥
# 📌 Test intent analysis base logic
#
# from InstructorEmbedding import INSTRUCTOR
#
# model = INSTRUCTOR('hkunlp/instructor-base', device="cpu")
#
# import numpy as np
# from sklearn.metrics.pairwise import cosine_similarity
#
# # general commands < 88
# # specific commands i.e. prompting, open apps < 90
#
# # command = 'search google for the current time in PHT'
# # command = 'make a google search for the current time in PHT'
# command = 'send relation to nora, Can you convert the following date time in PHT time zone?'
# # command = 'nora, summarize the time logs?'
# # command = 'Updated the instructor model to use the higher variation for better accuracy and also decreased the precision for semantic search to just float 16 instead of using the entire float 32 precision.'
#
# storage = 'represent tool descriptions document for retrieval: '
#
# query = [
#     ['represent question for retrieving relevant tool documents: ',
#      'What tool to use for this command: "' + command + '"']]
#
# original_array = [
#     "use the following tool for searching with google. command usually starts with 'search google'",
#     "use the following tool for asking requests to nora with context or relation. command usually starts with 'send relation to nora' or 'send context to nora'",
#     "use the following tool for asking nora to summarize a time log. example of the commands are: summarize time logs, format time logs",
#     "use the following tool for just describing something or elaborating on something that we want to transcribe."
# ]
#
# corpus = [[storage, item] for item in original_array]
#
# print(query)
# print(corpus)
#
# query_embeddings = model.encode(query)
# corpus_embeddings = model.encode(corpus)
# similarities = cosine_similarity(query_embeddings, corpus_embeddings)
# retrieved_doc_id = np.argmax(similarities)
# print(similarities)
# print(retrieved_doc_id)
