# Springfield Roleplay Community Discord Bot

A custom Discord bot for managing sessions, promotions, infractions, and staff administration for the Springfield Roleplay Community.

## Features

### Session Commands (IA+ Only)
- `/session start` - Announces a new session with server code
- `/session end` - Announces session shutdown
- `/session boost` - Requests player boost for low player count
- `/session vote` - Initiates a vote for session attendance

### Admin Commands (Administrator Only)
- `/promotion_issue` - Issues a promotion with embed
- `/infraction_issue` - Issues infractions with automatic warning/strike tracking
- `/say` - Makes the bot send a message

### Utility Commands
- `/infractions_check` - View a user's infraction history
- `/infractions_clear` - Clear a user's infraction record (Admin only)

## Setup Instructions

### 1. Prerequisites
- Python 3.8 or higher
- A Discord bot token from [Discord Developer Portal](https://discord.com/developers/applications)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` and fill in your values:
```
DISCORD_TOKEN=your_bot_token_here
GUILD_ID=your_server_id_here
SESSIONS_ROLE_ID=your_sessions_role_id_here
STAFF_TEAM_ROLE_ID=your_staff_team_role_id_here
INTERNAL_AFFAIRS_ROLE_ID=your_internal_affairs_role_id_here
```

### 4. Get Your IDs
- **Bot Token**: From Discord Developer Portal > Your Application > Bot > Token
- **Guild ID**: Enable Developer Mode in Discord > Right-click server > Copy ID
- **Role IDs**: Enable Developer Mode > Right-click role > Copy ID

### 5. Create Required Roles (Optional but Recommended)
For the infraction system to work automatically, create these roles in your server:
- `Warning 1`
- `Warning 2`
- `Warning 3`
- `Strike 1`
- `Strike 2`
- `Strike 3`

### 6. Invite Bot to Server
1. Go to Discord Developer Portal
2. Your Application > OAuth2 > URL Generator
3. Select scopes: `bot`, `applications.commands`
4. Select permissions: `Administrator`, `Send Messages`, `Embed Links`, `Manage Threads`, `Add Reactions`, `Manage Roles`
5. Copy generated URL and invite to your server

### 7. Run the Bot
```bash
python main.py
```

## Command Details

### Session Commands
**Permission**: Internal Affairs role OR Administrator

**/session start**
- Pings @Sessions and @Staff Team
- Embed: "A Session has begun by the Springfield Roleplay Community HR's. Join up!"
- Includes server code: sfrpj

**/session end**
- Silent announcement
- Embed: "The server is now shutdown. Do not join In-Game or you will be moderated."

**/session boost**
- Pings @Sessions and @Staff Team
- Embed: "A Session Boost has begun. We are low players. Join up!"

**/session vote**
- Pings @Sessions and @Staff Team
- Embed: "A Session is being initiated. Vote if you will join In-Game."
- Adds ✅ and ❌ reactions for voting

### Admin Commands
**Permission**: Administrator only

**/promotion_issue**
- Parameters:
  - staff_member: The staff member being promoted
  - issuer: The issuer of the promotion
  - reason: Reason for promotion
  - notes: Additional notes (optional)
- Creates a formatted embed with all details

**/infraction_issue**
- Parameters:
  - staff_member: The staff member being infracted
  - issuer: The issuer of the infraction
  - infraction_type: Verbal Warning, Warning, Strike, Termination, or Blacklist
  - reason: Reason for infraction
  - notes: Additional notes (optional)
- Automatically tracks warning levels (Warning 1, Warning 2, Warning 3)
- Automatically tracks strike levels (Strike 1, Strike 2, Strike 3)
- Assigns corresponding roles if they exist
- Creates a thread for appealing the infraction

**/say**
- Parameters:
  - message: The message for the bot to say
- Bot sends the message as-is

### Utility Commands

**/infractions_check**
- Parameters:
  - user: The user to check
- Shows warning and strike count for the user

**/infractions_clear** (Admin only)
- Parameters:
  - user: The user to clear infractions for
- Clears infraction record and removes associated roles

## Bot Profile
- **Name**: Springfield Roleplay Community
- **Status**: Moderating SFRP, Assisting Members, Moderating Staff
- **Description**: Always Moderating SFRP. Join today: .gg/sfrpj

## Troubleshooting

### Commands not appearing
- Make sure the bot has `applications.commands` scope
- Run the bot once to sync commands (may take up to an hour to propagate globally)
- Commands are synced to your specific guild for faster updates

### Permission errors
- Verify role IDs in `.env` are correct
- Ensure bot has Administrator permission in server
- Check that user has the required role/permissions

### Infraction roles not assigning
- Create the Warning 1-3 and Strike 1-3 roles in your server
- Ensure bot has "Manage Roles" permission
- Role hierarchy: Bot's role must be higher than warning/strike roles

## File Structure
```
Springfield Roleplay Community/
├── main.py              # Main bot code
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .env                 # Your actual environment variables (create this)
├── infractions.json     # Infraction data (auto-created)
└── README.md           # This file
```

## Deployment to Render

### Option 1: Using render.yaml (Recommended)

1. Push your code to a GitHub repository
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click **New +** > **Web Service**
4. Connect your GitHub repository
5. Render will automatically detect the `render.yaml` file
6. Configure the environment variables:
   - `DISCORD_TOKEN`: Your Discord bot token
   - `GUILD_ID`: Your server ID
   - `SESSIONS_ROLE_ID`: Sessions role ID
   - `STAFF_TEAM_ROLE_ID`: Staff Team role ID
   - `INTERNAL_AFFAIRS_ROLE_ID`: Internal Affairs role ID
7. Click **Deploy Web Service**

### Option 2: Manual Setup

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** > **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name**: springfield-discord-bot
   - **Region**: Choose nearest region
   - **Branch**: main
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
5. Add the same environment variables as above
6. Click **Deploy Web Service**

### Important Notes for Render

- The bot will run 24/7 on Render's free tier
- Render spins down services after 15 minutes of inactivity on free tier
- The bot will automatically restart when it receives a request
- For truly 24/7 uptime, consider upgrading to a paid plan
- Monitor logs in the Render Dashboard to troubleshoot issues

## Support
For issues or questions, contact the bot developer or check the Discord server.
