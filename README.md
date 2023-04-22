# WhisperingAssistant
A digital assistant powered by OpenAI's Whisper Transcription Service, designed to run on gaming laptop. This project aims to facilitate voice-based interactions, transcribe audio in real-time, and perform various tasks to enhance productivity and user experience.


## 📌 Clean Up
- Window manager common classes
- Class inheritance for commands
- Add all the commands supported one by one
- Short command logic
- Test the server.py

## 📌 Core Goals
**Primary**
- offline first. basic commands works offline
  - vision, transcription and small NLP agents, hotword detection
- complex task offloaded to online LLMs
- good caching, no need to repeat LLM calls for similar query
- shareable knowledge base (semantic search for common commands)

**Secondary**
- add a voice
- integrate with IoT devices



## 📌 Pending for MVP

- ⏳️ Embeddings for text commands
- ⏳️ create embeddings for the argument, perhaps some sort of caching for audio.
- ⏳ Move all UI to pyqt5

🚥🚥🚥 
- ✅ Commands
- Dictation Mode
- Plugin Development Archi
- ✅ Saving recordings locally for fine-tuning 
- ENV files
- Guide on dependency and what to install
- System requirements
- Redis/VectorDB for caching
- ChatGPT integration for intent parsing
- ✅ hot word detection integration