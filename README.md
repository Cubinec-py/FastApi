# FastAPI with TwitchIO service.
### Using this service you can interact with twitch users by playing their YouTube videos for their twitch channel points. Service can add and autoplay tracks from playlist, skip tracks by count 5 of command '!скип'. All interaction with tracks making by Celery tasks.

### Service can be run local and dev mode. To run it in any mode need to make this settings setup:

### ENV settings
Create .env file in source with environments:
```dotenv
SETTINGS=Dev/Local(Need to change depending on what mode you want to start service)

TWITCH_CHANNEL_ACCESS_TOKEN=Here need to put your user acces token(https://twitchtokengenerator.com)
TWITCH_CLIENT_SECRET=Here need to put your app secret(https://dev.twitch.tv/console)
USER_CHANNEL_ID=Here need to put your channel id(https://streamscharts.com/tools/convert-username)
TWITCH_REWARD_ADD_ID=Reward must be created by TwitchAPI
TWITCH_REWARD_SKIP_ID=Reward must be created by TwitchAPI
```
Create .env.dev file in source with environments:
```dotenv
DATABASE_URL=postgresql+asyncpg://DB user:DB password@DB host:DB port/DB name

POSTGRES_DB=DB name
POSTGRES_HOST=DB host
POSTGRES_PORT=DB port
POSTGRES_USER=DB user
POSTGRES_PASSWORD=DB password

REDIS_URL=redis://HOST:PORT

REDIS_HOST=
REDIS_PORT=

SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=

PGADMIN_DEFAULT_EMAIL=
PGADMIN_DEFAULT_PASSWORD=

TOKENS_SECRET_KEY=

HOST=Your server host
PORT=Your server port
SERVER_URL=http://Your server host:Your server port
WS_URL=ws://Your server host:Your server port
```
Create .env.local file in source with environments:
```dotenv
DATABASE_URL=postgresql+asyncpg://DB user:DB password@DB host:DB port/DB name

POSTGRES_DB=DB name
POSTGRES_HOST=DB host
POSTGRES_PORT=DB port
POSTGRES_USER=DB user
POSTGRES_PASSWORD=DB password

REDIS_URL=redis://HOST:PORT

REDIS_HOST=
REDIS_PORT=

SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=

PGADMIN_DEFAULT_EMAIL=
PGADMIN_DEFAULT_PASSWORD=

TOKENS_SECRET_KEY=

HOST=Your server host
PORT=Your server port
SERVER_URL=http://Your server host:Your server port
WS_URL=ws://Your server host:Your server port
```
### Running Local
To run project in local mode make SETTINGS=Local in .env.

Then need to set up local environment:
```bash
python3.10 -m venv .venv 
```
After set upping environment need to install requirements:
```bash
pip install -U pip
pip install -r requirements.txt
```
Migrate to set up local db:
```bash
alembic upgrade head
```
To start project use command:
```bash
uvicorn src.main:app
```
### Running Dev
To run project in dev mode make SETTINGS=Dev in .env.

To start project use command:
```bash
docker-compose up -d
```
### Additional information
To create Twitch reward use this: [TwitchAPI](https://dev.twitch.tv/docs/api/reference/#create-custom-rewards)

In order to be video displayed in OBS add new browser and put there link http://YOUR_HOST:YOUR_PORT(Or just your domain name)/api/v1/playlist/player

If some videos not available at startup, when you using it local or in dev and with ip address in host, need to change host name to any domain name, this is because YouTube do not pass addresses where host name is ip address.

