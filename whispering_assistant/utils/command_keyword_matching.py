import Levenshtein as lev
import numpy as np

from whispering_assistant.utils.commands_plugin_state import COMMAND_PLUGINS


def levenshtein_similarity(s1, s2):
    # Calculate the Levenshtein distance between two strings
    # Normalize it by dividing by the length of the longest string
    return (max(len(s1), len(s2)) - lev.distance(s1, s2)) / max(len(s1), len(s2))


def fuzzy_keyword_sequence_matching(input_text, keyword_string, similarity_threshold=0.80, position_threshold=1):
    input_text = input_text.lower().split()
    keywords = keyword_string.lower().split()

    max_similarities = []
    positions = []

    for i, keyword in enumerate(keywords):
        word_similarities = [(j, levenshtein_similarity(keyword, word)) for j, word in enumerate(input_text)]
        max_similarity_index, max_similarity = max(word_similarities, key=lambda x: x[1])
        positions.append(max_similarity_index)
        max_similarities.append(max_similarity)

    # Convert to a numpy array for convenience
    max_similarities_np = np.array(max_similarities)

    # Compute the minimum similarity
    min_similarity = np.min(max_similarities_np)
    print(f"Minimum similarity: {min_similarity}")

    # Compute the mean similarity
    mean_similarity = np.mean(max_similarities_np)
    print(f"Mean similarity: {mean_similarity}")

    print("positions", positions)

    # Check if the positions of the keywords in the text match the expected positions
    positions_match = all(abs(i - pos) <= position_threshold for i, pos in enumerate(positions))
    print(f"Positions match: {positions_match}")

    if mean_similarity > similarity_threshold and positions == sorted(positions) and positions_match:
        return True, mean_similarity

    return False, mean_similarity


def command_keyword_matching_top_match(input_text):
    collection = []
    for plugin in COMMAND_PLUGINS.values():
        if hasattr(plugin, 'keyword_match'):
            keyword_list = plugin.keyword_match.lower()
            is_match, similarity = fuzzy_keyword_sequence_matching(input_text, keyword_list)
            if is_match:
                # Append a tuple of the length of the keyword_list, similarity, and the plugin
                collection.append((len(keyword_list), similarity, plugin))
                print(f"Added plugin '{plugin}' with similarity {similarity} to collection.")
                collection.sort(reverse=True)
                if len(collection) == 3:
                    break
        else:
            pass
            # print(f"Plugin '{plugin}' does not have the attribute 'keyword_match'.")

    print(f"Final collection (top 3): {collection}")
    top_plugin = collection[0][2] if collection else None  # Note the change here
    print(f"Top plugin: {top_plugin}")
    return top_plugin
