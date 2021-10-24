# Setup

nio-template is a sample repository of a working Matrix bot that can be taken
and transformed into one's own bot, service or whatever else may be necessary.
Below is a quick setup guide to running the existing bot.

## Install the dependencies

There are two paths to installing the dependencies for development.


### Running natively

If you would rather not or are unable to run docker, the following will
instruct you on how to install the dependencies natively:

#### Install libolm

You can install [libolm](https://gitlab.matrix.org/matrix-org/olm) from source,
or alternatively, check your system's package manager. Version `3.0.0` or
greater is required.

**(Optional) postgres development headers**

By default, the bot uses SQLite as its storage backend. This is fine for a few
hundred users, but if you plan to support a much higher volume of requests, you
may consider using Postgres as a database backend instead.

If you want to use postgres as a database backend, you'll need to install
postgres development headers:

Debian/Ubuntu:

```
sudo apt install libpq-dev libpq5
```

Arch:

```
sudo pacman -S postgresql-libs
```

#### Install Python dependencies

Create and activate a Python 3 virtual environment:

```
virtualenv -p python3 env
source env/bin/activate
```

Install python dependencies:

```
pip install -e .
```

(Optional) If you want to use postgres as a database backend, use the following
command to install postgres dependencies alongside those that are necessary:

```
pip install -e ".[postgres]"
```
## Running


### Native installation

Make sure to source your python environment if you haven't already:

```
source env/bin/activate
```

Then simply run the bot with:

```
matrix-trivia-bot
```

You'll notice that "matrix-trivia-bot" is scattered throughout the codebase. When
it comes time to modifying the code for your own purposes, you are expected to
replace every instance of "matrix-trivia-bot" and its variances with your own
project's name.


## Testing the bot works

Invite the bot to a room and it should accept the invite and join.

By default nio-template comes with an `echo` command. Let's test this now.
After the bot has successfully joined the room, try sending the following
in a message:

```
!c echo I am a bot!
```

The message should be repeated back to you by the bot.

## Going forwards

Congratulations! Your bot is up and running. Now you can modify the code,
re-run the bot and see how it behaves. Have fun!

## Troubleshooting

If you had any difficulties with this setup process, please [file an
issue](https://github.com/anoadragon453/nio-template/issues]) or come talk
about it in [the matrix room](https://matrix.to/#/#nio-template).
