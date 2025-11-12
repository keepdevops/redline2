# User Data Storage & Access Guide

## Overview

REDLINE now supports **user-specific data storage** with complete data isolation. Each user's data is stored separately based on their license key, ensuring privacy and security.

## Storage Architecture

### 1. Local Storage (Default)
- **Location**: `data/users/{hashed_license_key}/`
- **Database**: `user_data.duckdb` per user
- **Files**: `files/` directory per user
- **Isolation**: Complete separation by license key

### 2. Cloud Storage (Optional - S3)
- **Provider**: Amazon S3
- **Structure**: `users/{hashed_license_key}/files/`
- **Backup**: Automatic sync to S3
- **Access**: Direct S3 access for large files

## How Data is Stored

### File Storage
When a user uploads or converts a file:
1. File is saved to: `data/users/{hash}/files/{filename}`
2. Metadata stored in: `data/users/{hash}/user_data.duckdb`
3. (Optional) Synced to S3: `s3://bucket/users/{hash}/files/{filename}`

### Database Storage
Each user has their own DuckDB database with tables:
- `user_files` - All uploaded files
- `converted_files` - Conversion history
- `user_data_tables` - Data table metadata

## User Data Access

### API Endpoints

#### List User Files
```bash
GET /user-data/files?license_key=RL-XXX
# Returns: List of all user's files
```

#### Upload File
```bash
POST /user-data/files/upload
Headers:
  X-License-Key: RL-XXX
  Content-Type: multipart/form-data
Body:
  file: <file data>
  file_type: csv
```

#### Get File Info
```bash
GET /user-data/files/{file_id}?license_key=RL-XXX
# Returns: File metadata and path
```

#### Download File
```bash
GET /user-data/files/{file_id}/download?license_key=RL-XXX
# Returns: File download
```

#### List Data Tables
```bash
GET /user-data/tables?license_key=RL-XXX
# Returns: List of user's data tables
```

#### Storage Statistics
```bash
GET /user-data/stats?license_key=RL-XXX
# Returns: Storage usage statistics
```

## Data Conversion Integration

When users convert files:
1. Original file is saved to user storage
2. Converted file is automatically saved to user storage
3. Conversion history is tracked in database
4. Both files remain accessible to the user

## Data Isolation

### Security Features
- **Hashed License Keys**: License keys are hashed before use in paths
- **No Cross-User Access**: Users can only access their own data
- **License Key Required**: All endpoints require valid license key

### Storage Structure
```
data/users/
├── {hash1}/          # User 1
│   ├── user_data.duckdb
│   └── files/
│       ├── file1.csv
│       └── file2.json
├── {hash2}/          # User 2
│   ├── user_data.duckdb
│   └── files/
│       └── file1.parquet
```

## Cloud Storage Setup (S3)

### Configuration
Add to `.env`:
```bash
USE_S3_STORAGE=true
S3_BUCKET=your-bucket-name
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_REGION=us-east-1
```

### Benefits
- **Backup**: Automatic backup to S3
- **Scalability**: No local storage limits
- **Access**: Direct S3 access for large files
- **Durability**: S3's 99.999999999% durability

## Accessing Existing Data

### For Users
1. **Via Web Interface**: Files are automatically saved when uploaded/converted
2. **Via API**: Use `/user-data/files` to list and download
3. **Via S3**: If S3 enabled, access files directly from S3

### Migration from Shared Storage
If you have existing data in shared storage:
1. Identify which license key owns which files
2. Use migration script to move files to user storage
3. Update database records

## Storage Limits

### Default Limits
- **No hard limit** on storage size
- **File count**: Unlimited
- **Table count**: Unlimited

### Recommended Limits (for billing)
- **Free tier**: 1 GB per user
- **Standard tier**: 10 GB per user
- **Professional tier**: 100 GB per user
- **Enterprise**: Unlimited

## Backup & Recovery

### Local Storage
- Files stored in `data/users/` directory
- Include in regular backups
- Database files can be backed up individually

### S3 Storage
- Automatic versioning (if enabled)
- Cross-region replication (if configured)
- Lifecycle policies for archival

## API Examples

### Upload and Convert
```python
import requests

license_key = "RL-XXXXXXXX-XXXXXXXX-XXXXXXXX"

# Upload file
with open('data.csv', 'rb') as f:
    response = requests.post(
        'http://localhost:8080/user-data/files/upload',
        headers={'X-License-Key': license_key},
        files={'file': f}
    )

# List files
response = requests.get(
    'http://localhost:8080/user-data/files',
    params={'license_key': license_key}
)
files = response.json()['files']

# Download file
file_id = files[0]['id']
response = requests.get(
    f'http://localhost:8080/user-data/files/{file_id}/download',
    params={'license_key': license_key}
)
```

## Files Created

- `redline/storage/user_storage.py` - User storage module
- `redline/web/routes/user_data.py` - User data API routes

## Files Modified

- `redline/web/routes/converter.py` - Auto-save converted files to user storage
- `web_app.py` - Registered user_data blueprint
- `env.template` - Added storage configuration
- `requirements.txt` - Added boto3 for S3 support

## Next Steps

1. **Set up S3** (optional) for cloud storage
2. **Configure storage limits** per license tier
3. **Add storage billing** based on usage
4. **Build migration tools** for existing data
5. **Add storage analytics** dashboard

