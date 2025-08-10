# Mangolo Configuration Reference (.mango files)

Mangolo uses TOML-based configuration files with the `.mango` extension to define project settings, environment variables, and runtime configuration. This document provides a comprehensive reference for all available configuration options.

## Table of Contents

- [Basic Structure](#basic-structure)
- [Project Configuration](#project-configuration)
- [Environment Configuration](#environment-configuration)
- [Server Configuration](#server-configuration)
- [Security Configuration](#security-configuration)
- [Frontend Configuration](#frontend-configuration)
- [Backend Configuration](#backend-configuration)
- [Database Configuration](#database-configuration)
- [Storage Configuration](#storage-configuration)
- [Email Configuration](#email-configuration)
- [Cache Configuration](#cache-configuration)
- [Logging Configuration](#logging-configuration)
- [Task Configuration](#task-configuration)
- [Advanced Configuration](#advanced-configuration)
- [Environment Variables](#environment-variables)
- [Examples](#examples)

## Basic Structure

A `.mango` file is organized into sections, each with related configuration options:

```toml
# Comments start with a hash symbol

[section]
key = "value"
another_key = 123

[another_section]
flag = true
list = ["item1", "item2"]
```

## Project Configuration

The `[project]` section defines basic information about your project.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `name` | string | | Project name |
| `version` | string | "1.0.0" | Project version |
| `description` | string | | Project description |
| `author` | string | | Author or organization name |
| `license` | string | | Project license |

```toml
[project]
name = "my-app"
version = "1.0.0"
description = "My awesome Mangolo project"
author = "Dev Team"
license = "MIT"
```

## Environment Configuration

The `[environment]` section defines runtime environment settings.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `production` | boolean | false | Whether the app is running in production mode |
| `debug` | boolean | true | Enable debug mode |
| `log_level` | string | "info" | Default logging level (debug, info, warn, error) |
| `timezone` | string | "UTC" | Default timezone for date operations |

```toml
[environment]
production = false
debug = true
log_level = "debug"
timezone = "America/New_York"
```

## Server Configuration

The `[server]` section configures the HTTP server.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `host` | string | "localhost" | Server hostname |
| `port` | integer | 8080 | Server port |
| `base_path` | string | "/" | Base URL path for all routes |
| `cors_enabled` | boolean | false | Enable CORS support |
| `cors_origins` | array | [] | Allowed origins for CORS |
| `rate_limit` | integer | 100 | Rate limit per minute per IP |
| `request_timeout` | integer | 30 | Request timeout in seconds |
| `upload_limit` | string | "10MB" | Maximum upload size |

```toml
[server]
host = "0.0.0.0"
port = 3000
base_path = "/api"
cors_enabled = true
cors_origins = ["https://example.com", "https://app.example.com"]
rate_limit = 200
request_timeout = 60
upload_limit = "50MB"
```

## Security Configuration

The `[security]` section manages authentication and security settings.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `jwt_secret` | string | | JWT signing secret |
| `token_expiry` | integer | 3600 | Token expiry in seconds |
| `refresh_token_expiry` | integer | 2592000 | Refresh token expiry in seconds (30 days) |
| `max_login_attempts` | integer | 5 | Maximum failed login attempts before lockout |
| `lockout_time` | integer | 900 | Account lockout time in seconds after failed attempts |
| `password_policy` | string | "medium" | Password policy (weak, medium, strong) |
| `allow_registration` | boolean | true | Allow user registration |
| `ssl_enabled` | boolean | false | Force SSL for all connections |

```toml
[security]
jwt_secret = "${ENV:JWT_SECRET}"
token_expiry = 7200
refresh_token_expiry = 604800
max_login_attempts = 3
lockout_time = 1800
password_policy = "strong"
allow_registration = true
ssl_enabled = true
```

## Frontend Configuration

The `[frontend]` section configures frontend-related settings.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `libs` | array | [] | Frontend libraries to use |
| `assets_dir` | string | "./assets" | Static assets directory |
| `templates_dir` | string | "./templates" | Templates directory |
| `public_dir` | string | "./public" | Public files directory |
| `cache_enabled` | boolean | true | Enable template caching |
| `minify` | boolean | false | Minify HTML/CSS/JS output |
| `spa` | boolean | false | Single Page Application mode |

```toml
[frontend]
libs = ["Vue", "TailwindCSS"]
assets_dir = "./src/assets"
templates_dir = "./src/templates"
public_dir = "./public"
cache_enabled = true
minify = true
spa = true
```

## Backend Configuration

The `[backend]` section configures server-side functionality.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `libs` | array | [] | Backend libraries to use |
| `extensions` | array | [] | Mangolo extensions to enable |
| `timeout` | integer | 30 | Function execution timeout in seconds |
| `workers` | integer | 4 | Number of worker processes |
| `max_memory` | string | "512MB" | Maximum memory usage per worker |

```toml
[backend]
libs = ["Python", "NodeJS"]
extensions = ["auth", "logging", "caching"]
timeout = 60
workers = 8
max_memory = "1GB"
```

## Database Configuration

The `[database]` section configures database connection and settings.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `type` | string | "json" | Database type (json, sqlite, mysql, postgresql, mongodb) |
| `url` | string | | Database connection URL |
| `host` | string | "localhost" | Database host |
| `port` | integer | | Database port |
| `name` | string | | Database name |
| `username` | string | | Database username |
| `password` | string | | Database password |
| `path` | string | "./data" | Path for file-based databases |
| `pool_size` | integer | 5 | Connection pool size |
| `max_connections` | integer | 10 | Maximum number of connections |
| `ssl_enabled` | boolean | false | Use SSL for database connection |
| `timeout` | integer | 30 | Connection timeout in seconds |
| `backup_frequency` | string | "daily" | Automatic backup frequency |

```toml
[database]
type = "postgresql"
host = "db.example.com"
port = 5432
name = "myapp"
username = "${ENV:DB_USER}"
password = "${ENV:DB_PASSWORD}"
pool_size = 10
max_connections = 20
ssl_enabled = true
backup_frequency = "daily"
```

## Storage Configuration

The `[storage]` section configures file storage options.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `provider` | string | "local" | Storage provider (local, s3, azure, gcs) |
| `uploads_dir` | string | "./uploads" | Local uploads directory |
| `bucket` | string | | Cloud storage bucket name |
| `region` | string | | Cloud storage region |
| `access_key` | string | | Cloud storage access key |
| `secret_key` | string | | Cloud storage secret key |
| `max_file_size` | string | "10MB" | Maximum individual file size |
| `allowed_types` | array | [] | Allowed file MIME types |
| `storage_limit` | string | "1GB" | Total storage limit |
| `public_url` | string | | Public base URL for stored files |

```toml
[storage]
provider = "s3"
bucket = "my-app-uploads"
region = "us-east-1"
access_key = "${ENV:AWS_ACCESS_KEY}"
secret_key = "${ENV:AWS_SECRET_KEY}"
max_file_size = "50MB"
allowed_types = ["image/jpeg", "image/png", "application/pdf"]
storage_limit = "10GB"
public_url = "https://cdn.example.com"
```

## Email Configuration

The `[email]` section configures email sending capabilities.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `provider` | string | "smtp" | Email provider (smtp, sendgrid, mailgun, ses) |
| `host` | string | "localhost" | SMTP host |
| `port` | integer | 25 | SMTP port |
| `username` | string | | SMTP username |
| `password` | string | | SMTP password |
| `from_address` | string | | Default sender email address |
| `from_name` | string | | Default sender name |
| `api_key` | string | | API key for email service providers |
| `templates_dir` | string | "./email_templates" | Email templates directory |
| `send_welcome_email` | boolean | true | Send welcome email on registration |
| `verify_ssl` | boolean | true | Verify SSL certificates |

```toml
[email]
provider = "sendgrid"
api_key = "${ENV:SENDGRID_API_KEY}"
from_address = "noreply@example.com"
from_name = "My App"
templates_dir = "./src/emails"
send_welcome_email = true
```

## Cache Configuration

The `[cache]` section configures caching behavior.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `enabled` | boolean | true | Enable caching |
| `driver` | string | "memory" | Cache driver (memory, redis, file) |
| `host` | string | "localhost" | Redis host |
| `port` | integer | 6379 | Redis port |
| `password` | string | | Redis password |
| `path` | string | "./cache" | Path for file-based cache |
| `ttl` | integer | 3600 | Default time-to-live in seconds |
| `max_size` | string | "100MB" | Maximum cache size |
| `prefix` | string | | Key prefix for all cache entries |

```toml
[cache]
enabled = true
driver = "redis"
host = "cache.example.com"
port = 6379
password = "${ENV:REDIS_PASSWORD}"
ttl = 7200
prefix = "myapp:"
```

## Logging Configuration

The `[logging]` section configures application logging.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `level` | string | "info" | Log level (debug, info, warn, error) |
| `format` | string | "json" | Log format (json, text) |
| `output` | string | "console" | Log output (console, file, both) |
| `file` | string | "./logs/app.log" | Log file path |
| `rotate` | boolean | true | Enable log rotation |
| `max_size` | string | "10MB" | Maximum log file size before rotation |
| `max_files` | integer | 5 | Maximum number of rotated log files to keep |
| `compress` | boolean | false | Compress rotated logs |

```toml
[logging]
level = "info"
format = "json"
output = "both"
file = "./logs/app.log"
rotate = true
max_size = "20MB"
max_files = 10
compress = true
```

## Task Configuration

The `[tasks]` section configures background task processing.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `queue_driver` | string | "local" | Queue driver (local, redis, sqs) |
| `queue_url` | string | | URL for remote queue services |
| `workers` | integer | 2 | Number of task workers |
| `max_retries` | integer | 3 | Maximum retries for failed tasks |
| `default_priority` | string | "normal" | Default task priority (low, normal, high) |
| `timeout` | integer | 60 | Task timeout in seconds |
| `rate_limit` | integer | 100 | Maximum tasks per minute |
| `scheduler_enabled` | boolean | false | Enable task scheduler |

```toml
[tasks]
queue_driver = "redis"
workers = 4
max_retries = 5
default_priority = "normal"
timeout = 120
rate_limit = 500
scheduler_enabled = true
```

## Advanced Configuration

The `[advanced]` section provides extension points and customization options.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `custom_middlewares` | array | [] | Custom middleware modules |
| `plugins` | array | [] | External plugins to load |
| `hooks` | object | {} | Event hook configurations |
| `metrics_enabled` | boolean | false | Enable performance metrics |
| `metrics_provider` | string | "prometheus" | Metrics provider |
| `health_check_path` | string | "/health" | Health check endpoint |
| `feature_flags` | object | {} | Feature flag definitions |

```toml
[advanced]
custom_middlewares = ["rate_limiter", "request_logger"]
plugins = ["my-plugin", "another-plugin"]
hooks = { "after_login" = "track_login_success", "before_delete" = "create_audit_log" }
metrics_enabled = true
metrics_provider = "datadog"
health_check_path = "/system/health"

[advanced.feature_flags]
new_ui = true
beta_features = false
```

## Environment Variables

You can reference environment variables in your configuration using `${ENV:VARIABLE_NAME}` syntax:

```toml
[database]
username = "${ENV:DB_USERNAME}"
password = "${ENV:DB_PASSWORD}"
```

You can also provide default values if an environment variable is not set:

```toml
[server]
port = "${ENV:PORT|8080}"  # Use PORT environment variable or default to 8080
```

## Examples

### Basic Project Configuration

```toml
[project]
name = "blog-api"
version = "1.0.0"
description = "Blog API with Mangolo"

[environment]
production = false
debug = true

[server]
port = 3000
base_path = "/api"

[database]
type = "sqlite"
path = "./data/blog.db"
```

### Production Configuration

```toml
[project]
name = "ecommerce"
version = "2.1.0"

[environment]
production = true
debug = false
log_level = "warn"

[server]
host = "0.0.0.0"
port = 80
cors_enabled = true
cors_origins = ["https://store.example.com"]
rate_limit = 500

[security]
jwt_secret = "${ENV:JWT_SECRET}"
token_expiry = 3600
ssl_enabled = true

[database]
type = "postgresql"
host = "${ENV:DB_HOST}"
port = 5432
name = "${ENV:DB_NAME}"
username = "${ENV:DB_USER}"
password = "${ENV:DB_PASSWORD}"
pool_size = 20

[cache]
driver = "redis"
host = "${ENV:REDIS_HOST}"
port = 6379

[email]
provider = "ses"
region = "us-west-2"
access_key = "${ENV:AWS_ACCESS_KEY}"
secret_key = "${ENV:AWS_SECRET_KEY}"
from_address = "orders@example.com"
```

### Microservice Configuration

```toml
[project]
name = "auth-service"
version = "1.0.0"

[environment]
production = true

[server]
host = "0.0.0.0"
port = 3001
base_path = "/auth"

[security]
jwt_secret = "${ENV:JWT_SECRET}"
token_expiry = 900  # 15 minutes

[database]
type = "mongodb"
url = "${ENV:MONGO_URL}"

[logging]
level = "info"
format = "json"

[advanced]
health_check_path = "/auth/health"
metrics_enabled = true
```
