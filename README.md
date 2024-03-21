# Requirements

- pycord
- whisper
- gpt4all
- configparser

# What this bot can do

You can ask the bot a question via text. Just type !askgpt and in quotations the question you want to ask. 
For example: `!askgpt "Is water a soup?"`

You can also do this via the voice chat:
First you need to be in a voice channel
Then type `!dialog X` with X being the number of seconds you will get to ask your question
It will then dynamically import the nessesary modules and tell you when you can speak
Then depending on the config.ini file it will generate an answer with the specified gpt model
After all that the bot will speak to you through the voice chat

Now this process will continue until you type `!stopdialog`
