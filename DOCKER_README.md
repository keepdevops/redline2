# REDLINE Web GUI Docker Deployment

Complete Docker deployment solution for REDLINE Web GUI using Ubuntu 24.04 LTS with modern features and full stack deployment.

## 🚀 Quick Start

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 2GB+ RAM
- 5GB+ disk space

### One-Command Deployment
```bash
# Clone and deploy
git clone <repository-url>
cd redline
./scripts/deploy.sh
```

### Access the Application
- **Web GUI**: http://localhost:8080
- **Nginx Proxy**: http://localhost:8081
- **Prometheus**: http://localhost:9090
- **Health Check**: http://localhost:8080/health

## 📁 Project Structure

```
redline/
├── Dockerfile                 # Ubuntu 24.04 LTS with Python 3.12
├── docker-compose.yml        # Full stack deployment
├── requirements.txt          # Python dependencies
├── web_app.py               # Flask web application
├── main.py                  # Tkinter GUI (for reference)
├── data_config.ini          # Application configuration
├── scripts/
│   ├── build.sh            # Docker image build script
│   ├── start.sh            # Container startup script
│   ├── shutdown.sh         # Graceful shutdown script
│   └── deploy.sh           # Complete deployment automation
├── config/                 # Configuration files
│   ├── nginx.conf
│   ├── redis.conf
│   ├── prometheus.yml
│   └── fluentd.conf
├── data/                   # Application data
├── logs/                   # Application logs
└── ssl/                    # SSL certificates (optional)
```

## 🐳 Docker Services

### Core Services
- **redline-web**: Main Flask application (Ubuntu 24.04 LTS)
- **redis**: Caching and session storage
- **nginx-proxy**: Reverse proxy and load balancer

### Monitoring Services
- **prometheus**: Metrics collection and monitoring
- **fluentd**: Log aggregation and processing

## 🛠️ Deployment Options

### Full Deployment
```bash
./scripts/deploy.sh
```

### Build Only
```bash
./scripts/deploy.sh --build-only
```

### Start Only
```bash
./scripts/deploy.sh --start-only
```

### Clean Deployment
```bash
./scripts/deploy.sh --clean --force
```

### Manual Docker Commands
```bash
# Build image
./scripts/build.sh

# Run container
./scripts/build.sh && ./run-container.sh

# Stop container
./stop-container.sh
```

## 🔧 Configuration

### Environment Variables
Create `.env` file with:
```bash
SECRET_KEY=your-secret-key
REDIS_PASSWORD=your-redis-password
FLASK_ENV=production
HOST=0.0.0.0
PORT=8080
```

### Nginx Configuration
- Main config: `config/nginx.conf`
- Site config: `config/nginx-site.conf`
- SSL support: Place certificates in `ssl/` directory

### Redis Configuration
- Config file: `config/redis.conf`
- Memory limit: 256MB
- Persistence: Enabled
- Password: Configurable

## 📊 Monitoring

### Health Checks
- Application: `curl http://localhost:8080/health`
- Redis: `docker-compose exec redis redis-cli ping`
- Nginx: `curl http://localhost:8081/health`

### Metrics
- Prometheus: http://localhost:9090
- Application metrics: http://localhost:8080/metrics
- System metrics: Available via Prometheus

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f redline-web
docker-compose logs -f redis
docker-compose logs -f nginx-proxy

# View log files
tail -f logs/app/app.log
tail -f logs/nginx/access.log
```

## 🔒 Security Features

### Container Security
- Non-root user execution
- Read-only root filesystem
- No new privileges
- Resource limits
- Security options

### Network Security
- Isolated network
- Internal service communication
- External port exposure only where needed

### Application Security
- Secret key management
- Redis password protection
- HTTPS support (with SSL certificates)
- Input validation and sanitization

## 🚀 Performance Features

### Ubuntu 24.04 LTS Features
- Python 3.12 with latest optimizations
- Modern package management
- Systemd integration
- Snap and Flatpak support
- Advanced security features

### Application Performance
- Gunicorn with gevent workers
- Redis caching
- Nginx reverse proxy
- Static file optimization
- Database connection pooling

### Resource Management
- Memory limits: 2GB per container
- CPU limits: 2 cores per container
- Disk space monitoring
- Automatic cleanup

## 📝 Management Commands

### Service Management
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Scale services
docker-compose up -d --scale redline-web=2
```

### Container Management
```bash
# View running containers
docker-compose ps

# View resource usage
docker stats

# Execute commands in container
docker-compose exec redline-web /bin/bash
docker-compose exec redis redis-cli
```

### Log Management
```bash
# Follow logs
docker-compose logs -f

# View specific service logs
docker-compose logs redline-web

# Clean up logs
docker system prune -f
```

## 🔄 Updates and Maintenance

### Update Application
```bash
# Pull latest changes
git pull

# Rebuild and restart
./scripts/deploy.sh --clean --force
```

### Backup Data
```bash
# Backup data directory
tar -czf redline-backup-$(date +%Y%m%d).tar.gz data/

# Backup database
docker-compose exec redline-web python3 -c "
import duckdb
conn = duckdb.connect('/opt/redline/data/redline_data.duckdb')
conn.execute('EXPORT DATABASE \"/backup/redline_db\"')"
```

### Cleanup
```bash
# Clean up containers and images
docker-compose down -v --remove-orphans
docker system prune -af

# Clean up logs
find logs/ -name "*.log" -mtime +7 -delete
```

## 🐛 Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check logs
docker-compose logs redline-web

# Check resource usage
docker stats

# Check disk space
df -h
```

#### Application Not Responding
```bash
# Check health endpoint
curl http://localhost:8080/health

# Check service status
docker-compose ps

# Restart services
docker-compose restart
```

#### Database Issues
```bash
# Check database file permissions
ls -la data/redline_data.duckdb

# Recreate database
rm data/redline_data.duckdb
docker-compose restart redline-web
```

### Debug Mode
```bash
# Enable debug mode
export FLASK_DEBUG=true
docker-compose up -d

# View debug logs
docker-compose logs -f redline-web
```

## 📚 Additional Resources

### Documentation
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Ubuntu 24.04 LTS Documentation](https://ubuntu.com/server/docs)

### Support
- Check logs for error messages
- Review configuration files
- Test individual components
- Use health check endpoints

## 🎯 Production Deployment

### Production Checklist
- [ ] Set strong SECRET_KEY
- [ ] Configure Redis password
- [ ] Set up SSL certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring alerts
- [ ] Configure log rotation
- [ ] Set up backup strategy
- [ ] Test disaster recovery

### Scaling
```bash
# Scale web application
docker-compose up -d --scale redline-web=3

# Add load balancer
# Configure nginx for multiple backends
```

### High Availability
- Use Docker Swarm or Kubernetes
- Set up database replication
- Configure health checks
- Implement circuit breakers
- Set up monitoring and alerting

---

**REDLINE Web GUI Docker Deployment** - Modern, secure, and scalable financial data analysis platform.
