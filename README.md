# WhisperingAssistant
A digital assistant powered by OpenAI's Whisper Transcription Service, designed to run on gaming laptop. This project aims to facilitate voice-based interactions, transcribe audio in real-time, and perform various tasks to enhance productivity and user experience.


## 📌 How to install
- Install conda (23.3.1)
- Use the script to install dependencies for conda and pip
```commandline
./install.sh
```

## 📌 TODOs
- Add support for dynamic prompting and better prompting depending on the context.
  - We can use different parameters like the current active window, the content of the clipboard, some keywords used or detected during the first 4 seconds of transcription.
- Support on GPT for continuing the conversation instead of just creating a new one.
- Custom cut off time based on command type
- If transcription is done in quick succession, it could mean that the previous transcription is incorrect.
- Pass false positive hot-word to ASR
- Automatic muting of hot-word

## 📌 Clean Up
- Specify all the versions for all the dependencies to make sure that the project is easily replicable even in the future.
- Clean up hard coded dirs
- Clean up ReadMe file 
  - System requirements
  - Specify all the assumptions and dependencies being used in the project.
- Allow all configuration files to be operating by using the .env file

## 📌 Core Goals
**Primary**
- Offline first. basic commands works offline
  - vision, transcription and small NLP agents, hotword detection
- Complex task offloaded to online LLMs
- Good caching, no need to repeat LLM calls for similar query (📍 It might be better to just put this on another repository which just focuses on this feature.)
- Shareable knowledge base (semantic search for common commands)

**Secondary**
- Add a voice (TTS)
- Integrate with IoT devices

## 📌 Nice to haves
- ⏳️ Embeddings for text commands
- ⏳️ Create embeddings for the argument, perhaps some sort of caching for audio.
- Move all UI to pyqt5
- Dictation Mode
- Redis/VectorDB for caching
- ChatGPT's integration for intent parsing
