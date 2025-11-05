# Deployment Guide

This guide explains how to deploy the OpenHPI Automation Platform using Docker.

## Prerequisites

- Docker Engine 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose V2+ ([Install Compose](https://docs.docker.com/compose/install/))
- At least 2GB of available RAM
- 5GB of available disk space

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/siddhant61/openhpi-automate.git
cd openhpi-automate
```

### 2. Configure Environment

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and set your credentials:

```env
# OpenHPI Platform Credentials
OPENHPI_USERNAME=your-username
OPENHPI_PASSWORD=your-password

# Google AI (for analysis features)
GOOGLE_API_KEY=your-api-key

# Database (optional - defaults are provided)
POSTGRES_USER=openhpi
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=openhpi_automation

# Optional: Notifications
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 3. Start the Services

```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Access the Platform

Once all services are healthy (check with `docker-compose ps`):

- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Streamlit Dashboard**: http://localhost:8501
- **Database**: localhost:5432 (PostgreSQL)

## Service Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   Streamlit     │────▶│   FastAPI       │
│   Dashboard     │     │   Backend       │
│   (Port 8501)   │     │   (Port 8000)   │
└─────────────────┘     └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   PostgreSQL    │
                        │   Database      │
                        │   (Port 5432)   │
                        └─────────────────┘
```

## Service Management

### Start Services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d api
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes database)
docker-compose down -v
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart api
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f dashboard
docker-compose logs -f db
```

### Update Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose build
docker-compose up -d
```

## Database Management

### Initialize Database

The database is automatically initialized on first startup. To manually reinitialize:

```bash
docker-compose exec api python -m src.cli init
```

### Database Migrations

Run Alembic migrations:

```bash
# Check current version
docker-compose exec api alembic current

# Upgrade to latest
docker-compose exec api alembic upgrade head

# Create new migration
docker-compose exec api alembic revision --autogenerate -m "Description"
```

### Backup Database

```bash
# Backup to file
docker-compose exec db pg_dump -U openhpi openhpi_automation > backup.sql

# Restore from backup
docker-compose exec -T db psql -U openhpi openhpi_automation < backup.sql
```

## CLI Access

Run CLI commands inside the container:

```bash
# Access CLI
docker-compose exec api python -m src.cli --help

# Example: Scrape courses
docker-compose exec api python -m src.cli scrape courses

# Example: View configuration
docker-compose exec api python -m src.cli config

# Example: Generate analytics
docker-compose exec api python -m src.cli analytics annual 2024
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENHPI_USERNAME` | OpenHPI platform username | `user@example.com` |
| `OPENHPI_PASSWORD` | OpenHPI platform password | `SecurePass123` |
| `GOOGLE_API_KEY` | Google AI API key for analysis | `AIza...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | Database username | `openhpi` |
| `POSTGRES_PASSWORD` | Database password | `changeme` |
| `POSTGRES_DB` | Database name | `openhpi_automation` |
| `API_PORT` | API server port | `8000` |
| `DASHBOARD_PORT` | Dashboard port | `8501` |
| `API_WORKERS` | Number of API workers | `4` |
| `ENV` | Environment mode | `production` |
| `DEBUG` | Debug mode | `false` |

## Monitoring

### Health Checks

All services have health checks configured:

```bash
# Check service health
docker-compose ps

# API health endpoint
curl http://localhost:8000/health

# Dashboard health endpoint
curl http://localhost:8501/_stcore/health
```

### Resource Usage

```bash
# View resource usage
docker stats

# View specific service
docker stats openhpi-api
```

## Troubleshooting

### Services Won't Start

1. Check logs: `docker-compose logs -f`
2. Verify .env file is configured correctly
3. Ensure ports 8000, 8501, 5432 are not in use
4. Check Docker daemon is running

### Database Connection Issues

```bash
# Test database connection
docker-compose exec api python -c "from src.models.database import engine; print(engine.url)"

# Check database is running
docker-compose exec db psql -U openhpi -d openhpi_automation -c "SELECT 1;"
```

### API Not Responding

```bash
# Check API logs
docker-compose logs -f api

# Verify API is healthy
curl http://localhost:8000/health

# Restart API
docker-compose restart api
```

### Dashboard Not Loading

```bash
# Check dashboard logs
docker-compose logs -f dashboard

# Verify Streamlit is running
curl http://localhost:8501/_stcore/health

# Restart dashboard
docker-compose restart dashboard
```

## Production Deployment

### Security Recommendations

1. **Change default passwords** in `.env`
2. **Use strong passwords** for database
3. **Enable HTTPS** using a reverse proxy (nginx, traefik)
4. **Set `DEBUG=false`** in production
5. **Restrict database port** exposure (remove from `ports:` in docker-compose.yml)
6. **Use secrets management** for sensitive data

### Reverse Proxy Setup (nginx example)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Performance Tuning

```yaml
# docker-compose.yml additions
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

## Backup and Recovery

### Full System Backup

```bash
# Backup database
docker-compose exec db pg_dump -U openhpi openhpi_automation > db_backup.sql

# Backup volumes
docker run --rm -v openhpi-automate_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_data.tar.gz /data
```

### Recovery

```bash
# Restore database
docker-compose exec -T db psql -U openhpi openhpi_automation < db_backup.sql
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/siddhant61/openhpi-automate/issues
- Documentation: See README.md

## License

MIT License - See LICENSE file for details
