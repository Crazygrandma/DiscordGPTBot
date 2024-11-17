# DiscordGPTBot

Welcome to **DiscordGPTBot**, a feature-rich Discord bot built with the [Pycord](https://github.com/Pycord-Development/pycord) API and integrated with a local LLM (Large Language Model). This bot is designed to make your Discord experience more interactive, fun, and developer-friendly with a wide range of features.

## Features

- **Chat with a Local LLM**: Interact with a locally hosted language model for intelligent and dynamic conversations directly within Discord.
  
- **Custom Audio Playback**: Play custom audio files in voice channels for more engaging interactions.

- **Basic Development Reload**: Reload the bot's commands and settings on the fly, making development and debugging faster and more efficient.

- **Planned Features**:
    - **Voice-to-LLM Interaction**: A system to communicate with the local LLM through Discord's voice chat, powered by the [Whisper module](https://github.com/openai/whisper).
    - More to come as the bot evolves!

## Installation

To get started with **DiscordGPTBot**, follow the steps below.

### Prerequisites

1. Python 3.8+ is required.
2. You'll need a **Discord Bot Token**. You can get one by following the instructions [here](https://discord.com/developers/docs/intro).
3. A **local LLM** setup (e.g., GPT-based model) running on your machine or accessible via an API.

### Clone the Repository

```bash
git clone https://github.com/yourusername/DiscordGPTBot.git
cd DiscordGPTBot
```

### Install Dependencies
```bash
pip install -r requirements.txt
```
### Set Up Environment Variables
```bash
DISCORD_TOKEN=your_discord_token
LLM_API_KEY=your_llm_api_key # If using an external LLM
```
### Run the Bot
```bash
python main.py
```

### Usage
Once the bot is running, you can invite it to your Discord server and use the following commands:
- ```/askgpt [message]``` Chat with the local LLM.
- ```/play [file-name] ```Play a custom audio file in the voice channel.
- ```/reload``` Reload the bot’s commands and settings (useful for developers).

### Contributing

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
