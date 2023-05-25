# from whispering_assistant.commands import execute_plugin_by_keyword
# from whispering_assistant.commands.gpt_talk_with_clipboard_context import get_best_match

# use this to do some testing for plugin execution based on the transcript created.
# execute_plugin_by_keyword("send relation to ruby. use better prompts helper. I need to make an update to our existing application to add the new feature for calendar integration.")

# 🚥🚥🚥
# 📌 Test difflib threshold

# best_match = get_best_match(query="nora, create a checklist",
#                             items=[{'sample_command': ["create a checklist"]}])
# print(best_match)

# 🚥🚥🚥
# 📌 Test intent analysis logic per plugin

# result_text = "send relation to nora. Can you convert the following date time in PHT time zone?"
# # result_text = "lock screen 11"
# execute_plugin_by_keyword(result_text, skip_fallback=True, run_command=False)

# 🚥🚥🚥
# 📌 Test intent analysis base logic

from InstructorEmbedding import INSTRUCTOR

model = INSTRUCTOR('hkunlp/instructor-large')

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# general commands < 88
# specific commands i.e. prompting, open apps < 90

# command = 'search google for the current time in PHT'
# command = 'make a google search for the current time in PHT'
# command = 'send relation to nora, Can you convert the following date time in PHT time zone?'
# command = 'nora, summarize the time logs?'
command = 'Updated the instructor model to use the higher variation for better accuracy and also decreased the precision for semantic search to just float 16 instead of using the entire float 32 precision.'

storage = 'represent tool descriptions document for retrieval: '

query = [
    ['represent question for retrieving relevant tool documents: ',
     'What tool to use for this command: "' + command + '"']]

original_array = [
    "use the following tool for searching with google. command usually starts with 'search google'",
    "use the following tool for asking requests to nora with context or relation. command usually starts with 'send relation to nora' or 'send context to nora'",
    "use the following tool for asking nora to summarize a time log. example of the commands are: summarize time logs, format time logs",
    "use the following tool for just describing something or elaborating on something that we want to transcribe."
]

corpus = [[storage, item] for item in original_array]

print(query)
print(corpus)

query_embeddings = model.encode(query)
corpus_embeddings = model.encode(corpus)
similarities = cosine_similarity(query_embeddings, corpus_embeddings)
retrieved_doc_id = np.argmax(similarities)
print(similarities)
print(retrieved_doc_id)
