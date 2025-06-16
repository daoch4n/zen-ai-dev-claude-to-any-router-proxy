# Production Deployment Guide

## OpenRouter Anthropic Server v2.0 - Production Deployment

This guide covers deploying the OpenRouter Anthropic Server v2.0 to production environments.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.10 or higher
- **Memory**: Minimum 512MB RAM, recommended 1GB+
- **CPU**: 1+ cores (2+ recommended for production)
- **Storage**: 1GB+ available space
- **Network**: Outbound HTTPS access to OpenRouter API

### Dependencies
- **uv** (Python package manager)
- **FastAPI** with ASGI server (Uvicorn)
- **LiteLLM** for API integration
- **Instructor** for structured outputs

## 🚀 Deployment Options

### Option 1: Direct Server Deployment

#### 1. Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd claude-code-proxy

# Install dependencies
uv sync

# Set environment variables
export OPENROUTER_API_KEY="your-api-key-here"
export ENVIRONMENT="production"
export LOG_LEVEL="INFO"
export PORT="4000"
export HOST="0.0.0.0"
```

#### 2. Production Configuration
Create `.env` file:
```env
# API Configuration
OPENROUTER_API_KEY=your-openrouter-api-key
ENVIRONMENT=production

# Unified Proxy Backend Configuration
# Options: OPENROUTER, AZURE_DATABRICKS, LITELLM_OPENROUTER
PROXY_BACKEND=OPENROUTER

# Azure Databricks Configuration (only if PROXY_BACKEND=AZURE_DATABRICKS)
# DATABRICKS_HOST=your-workspace-instance
# DATABRICKS_TOKEN=your-databricks-token

# LiteLLM Configuration (only if PROXY_BACKEND=LITELLM_OPENROUTER) 
# LITELLM_MASTER_KEY=your-secure-master-key

# Server Configuration
HOST=0.0.0.0
PORT=4000
LOG_LEVEL=INFO

# Model Mapping
ANTHROPIC_MODEL=anthropic/claude-sonnet-4
ANTHROPIC_SMALL_FAST_MODEL=anthropic/claude-3.7-sonnet

# Performance Settings
MAX_TOKENS=4096
INSTRUCTOR_TEMPERATURE=0.1
CACHE_TTL=3600

# Security
DEBUG_ENABLED=false
INSTRUCTOR_ENABLED=true
```

#### 3. Start Production Server
```bash
# Using uv
uv run uvicorn src.main:app --host 0.0.0.0 --port 4000 --workers 4

# Or using Python directly
python -m uvicorn src.main:app --host 0.0.0.0 --port 4000 --workers 4
```

### Option 2: Docker Deployment

#### 1. Create Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY src/ ./src/
COPY docs/ ./docs/
COPY tests/ ./tests/

# Expose port
EXPOSE 4000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:4000/health || exit 1

# Start server
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "4000", "--workers", "4"]
```

#### 2. Build and Run
```bash
# Build image
docker build -t openrouter-anthropic-server:v2.0 .

# Run container with OpenRouter backend (recommended)
docker run -d \
  --name openrouter-server \
  -p 4000:4000 \
  -e OPENROUTER_API_KEY=your-api-key \
  -e PROXY_BACKEND=OPENROUTER \
  -e ENVIRONMENT=production \
  openrouter-anthropic-server:v2.0

# Or with Azure Databricks backend
docker run -d \
  --name openrouter-server \
  -p 4000:4000 \
  -e OPENROUTER_API_KEY=your-api-key \
  -e PROXY_BACKEND=AZURE_DATABRICKS \
  -e DATABRICKS_HOST=your-workspace-instance \
  -e DATABRICKS_TOKEN=your-databricks-token \
  -e ENVIRONMENT=production \
  openrouter-anthropic-server:v2.0
```

### Option 3: Docker Compose

#### docker-compose.yml
```yaml
version: '3.8'

services:
  openrouter-server:
    build: .
    ports:
      - "4000:4000"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - PROXY_BACKEND=${PROXY_BACKEND:-OPENROUTER}
      - DATABRICKS_HOST=${DATABRICKS_HOST}
      - DATABRICKS_TOKEN=${DATABRICKS_TOKEN}
      - LITELLM_MASTER_KEY=${LITELLM_MASTER_KEY}
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - DEBUG_ENABLED=false
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - openrouter-server
    restart: unless-stopped
```

## 🔧 Configuration

### Backend Mode Selection

The server supports three backend modes for different production scenarios:

#### **OPENROUTER** (Recommended for most deployments)
- **Performance**: Fastest response times with direct API calls
- **Complexity**: Minimal configuration required
- **Use Case**: Standard production deployments
```env
PROXY_BACKEND=OPENROUTER
OPENROUTER_API_KEY=your-api-key
```

#### **AZURE_DATABRICKS** (Enterprise Azure environments)
- **Performance**: Direct integration with Azure Databricks Claude endpoints
- **Complexity**: Requires Azure Databricks Premium workspace setup
- **Use Case**: Azure-native deployments with Databricks infrastructure
```env
PROXY_BACKEND=AZURE_DATABRICKS
DATABRICKS_HOST=your-workspace-instance
DATABRICKS_TOKEN=your-databricks-token
OPENROUTER_API_KEY=your-api-key  # For fallback tools
```

#### **LITELLM_OPENROUTER** (Advanced features needed)
- **Performance**: Additional overhead but advanced features available
- **Complexity**: Requires LiteLLM configuration and master key
- **Use Case**: When caching, load balancing, or advanced routing is needed
```env
PROXY_BACKEND=LITELLM_OPENROUTER
OPENROUTER_API_KEY=your-api-key
LITELLM_MASTER_KEY=your-secure-master-key
```

### Environment Variables

| Variable                     | Required | Default                       | Description                                                     |
| ---------------------------- | -------- | ----------------------------- | --------------------------------------------------------------- |
| `OPENROUTER_API_KEY`         | ✅        | -                             | OpenRouter API key                                              |
| `PROXY_BACKEND`              | ❌        | `OPENROUTER`                  | Backend mode (OPENROUTER, AZURE_DATABRICKS, LITELLM_OPENROUTER) |
| `DATABRICKS_HOST`            | ❌        | -                             | Azure Databricks workspace instance (if using AZURE_DATABRICKS) |
| `DATABRICKS_TOKEN`           | ❌        | -                             | Azure Databricks PAT token (if using AZURE_DATABRICKS)          |
| `LITELLM_MASTER_KEY`         | ❌        | -                             | LiteLLM master key (if using LITELLM_OPENROUTER)                |
| `ENVIRONMENT`                | ❌        | `development`                 | Environment mode                                                |
| `HOST`                       | ❌        | `127.0.0.1`                   | Server host                                                     |
| `PORT`                       | ❌        | `4000`                        | Server port                                                     |
| `LOG_LEVEL`                  | ❌        | `INFO`                        | Logging level                                                   |
| `DEBUG_ENABLED`              | ❌        | `false`                       | Debug logging                                                   |
| `INSTRUCTOR_ENABLED`         | ❌        | `true`                        | Structured outputs                                              |
| `ANTHROPIC_MODEL`            | ❌        | `anthropic/claude-sonnet-4`   | Large model mapping                                             |
| `ANTHROPIC_SMALL_FAST_MODEL` | ❌        | `anthropic/claude-3.7-sonnet` | Small model mapping                                             |

### Performance Tuning

#### Worker Configuration
```bash
# For CPU-bound workloads
uvicorn src.main:app --workers $(nproc)

# For I/O-bound workloads (recommended)
uvicorn src.main:app --workers $(($(nproc) * 2 + 1))
```

#### Memory Optimization
```bash
# Set memory limits
export PYTHONMALLOC=malloc
export MALLOC_ARENA_MAX=2
```

## 🔒 Security

### SSL/TLS Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        proxy_pass http://openrouter-server:4000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### API Key Security
- Store API keys in environment variables or secrets management
- Never commit API keys to version control
- Use different API keys for different environments
- Implement API key rotation procedures

### Network Security
- Use HTTPS in production
- Implement rate limiting
- Configure firewall rules
- Use VPC/private networks when possible

## 📊 Monitoring

### Health Checks
```bash
# Basic health check
curl http://localhost:4000/health

# Detailed health check
curl http://localhost:4000/health/detailed
```

### Logging
- Logs are structured JSON format
- Configure log aggregation (ELK, Splunk, etc.)
- Set up log rotation
- Monitor error rates and response times

### Metrics
- Request/response metrics via middleware
- Performance tracking
- Error rate monitoring
- Resource utilization

## 🔄 Deployment Strategies

### Blue-Green Deployment
1. Deploy new version to green environment
2. Run health checks and tests
3. Switch traffic from blue to green
4. Keep blue as rollback option

### Rolling Deployment
1. Deploy to subset of instances
2. Verify functionality
3. Gradually roll out to all instances
4. Monitor throughout process

### Canary Deployment
1. Deploy to small percentage of traffic
2. Monitor metrics and errors
3. Gradually increase traffic percentage
4. Full rollout or rollback based on metrics

## 🚨 Troubleshooting

### Common Issues

#### Server Won't Start
```bash
# Check logs
docker logs openrouter-server

# Verify environment variables
env | grep OPENROUTER

# Test configuration
uv run python -c "from src.utils.config import config; print(config)"
```

#### API Errors
```bash
# Check API key
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/models

# Verify connectivity
curl http://localhost:4000/health
```

#### Performance Issues
- Monitor CPU and memory usage
- Check network latency to OpenRouter API
- Review log files for errors
- Adjust worker count based on load

### Log Analysis
```bash
# Filter error logs
docker logs openrouter-server 2>&1 | grep ERROR

# Monitor request patterns
docker logs openrouter-server 2>&1 | grep "📨 Incoming request"
```

## 📈 Scaling

### Horizontal Scaling
- Deploy multiple instances behind load balancer
- Use container orchestration (Kubernetes, Docker Swarm)
- Implement session affinity if needed

### Vertical Scaling
- Increase CPU and memory resources
- Adjust worker count
- Optimize application configuration

### Load Balancing
```nginx
upstream openrouter_backend {
    server openrouter-server-1:4000;
    server openrouter-server-2:4000;
    server openrouter-server-3:4000;
}

server {
    location / {
        proxy_pass http://openrouter_backend;
    }
}
```

## 🔧 Maintenance

### Updates
1. Test updates in staging environment
2. Create backup/rollback plan
3. Deploy during maintenance window
4. Monitor post-deployment

### Backup
- Configuration files
- Environment variables
- SSL certificates
- Application logs (if needed)

### Monitoring Checklist
- [ ] Health endpoint responding
- [ ] API requests succeeding
- [ ] Error rates within acceptable limits
- [ ] Response times acceptable
- [ ] Resource utilization normal
- [ ] Logs being generated properly

## 📞 Support

For production issues:
1. Check health endpoints
2. Review application logs
3. Verify OpenRouter API status
4. Check network connectivity
5. Review configuration settings

## 🎯 Production Checklist

- [ ] Environment variables configured
- [ ] SSL/TLS certificates installed
- [ ] Health checks configured
- [ ] Monitoring and alerting set up
- [ ] Backup procedures in place
- [ ] Security measures implemented
- [ ] Performance testing completed
- [ ] Rollback procedures documented
- [ ] Team trained on deployment process
- [ ] Documentation updated