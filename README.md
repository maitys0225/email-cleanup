# Email Cleanup with Local LLM

This project combines a local LLM (Language Learning Model) setup with Gmail API access to automatically identify and delete promotional emails from your inbox.

## Setup Instructions

### 1. Create Project Structure

```bash
mkdir email-usecase
cd email-usecase
mkdir -p models
mkdir -p ollama-data
mkdir -p open-webui-data
```

### 2. Create docker-compose.yml

Create a file named `docker-compose.yml` with this content:

```yaml
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ./ollama-data:/root/.ollama
    restart: unless-stopped

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "8089:8080"
    volumes:
      - ./open-webui-data:/app/backend/data
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - ollama
    restart: unless-stopped
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

### 3. Start Docker Containers

```bash
docker-compose up -d
```

This will start both Ollama (local LLM server) and Open WebUI (web interface).

### 4. Install Required Python Packages

```bash
python3 -m pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib requests
```

### 5. Set Up Google API Credentials

1. Visit the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Navigate to "APIs & Services" > "Library"
4. Search for and enable the Gmail API
5. Go to "APIs & Services" > "Credentials"
6. Click "Create Credentials" > "OAuth client ID"
7. Select "Desktop application" as the application type
8. Download the credentials as `credentials.json` and place it in your project directory
9. Go to "APIs & Services" > "OAuth consent screen"
10. Add your email address as a test user

### 6. Create the Gmail Cleanup Script

Create a file named `gmail_cleanup.py` with this content:

### 7. Download a Model (Optional)

Ollama will download models automatically when needed, but you can pre-download:

```bash
curl -X POST http://localhost:11434/api/pull -d '{"name": "tinyllama"}'
```

### 8. Run the Cleanup Script

```bash
python3 gmail_cleanup.py
```

The first time you run this, it will open a browser window for you to authenticate with your Google account.

## Usage

- The script will process up to 20 emails at a time (configurable by changing the `max_emails` parameter)
- Emails classified as promotional will be moved to trash
- Important emails will remain in your inbox
- Run the script periodically to keep your inbox clean

## Web Interface

Access the Open WebUI interface at http://localhost:8089 to interact with your local LLM directly.

## Stopping and Restarting

To stop all containers:
```bash
docker-compose down
```

To restart:
```bash
docker-compose up -d
```

## Project Files

- `docker-compose.yml` - Container configuration
- `credentials.json` - Google API credentials (obtained from Google Cloud Console)
- `gmail_cleanup.py` - Email processing script
- `token.pickle` - Stores OAuth token (created automatically)
- `ollama-data/` - Stores Ollama models and data
- `open-webui-data/` - Stores OpenWebUI configuration and history