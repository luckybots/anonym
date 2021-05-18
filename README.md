# Anonym

Telegram bot that anonymizes messages in chats. Give bot an admin permission to delete messages in your chat.

# How to use Anonym

You can either use an existing Anonym bot available at https://t.me/anonym10_bot. In order to do that:

1. Give Anonym bot an admin permission to delete messages in your chat.

# Build Anonym from sources

To build your own version of Anonym:

1. Download the source code
```
git clone --recurse-submodules https://github.com/luckybots/anonym.git
```
If you don't add --recurse-submodules -- you'll get an error during make build (make: *** No rule to make target 'build')

2. Create and customize `data/config.json` according to `data/config_example.json`. In the `config.json` provide `bot_token` value.
   
3. To run with Docker use
```
make build
make run-it
```
