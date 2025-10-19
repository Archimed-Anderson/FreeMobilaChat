# 💾 Production Backup System Guide

## Overview
This guide covers the automated backup system for the FreeMobilaChat application, including database backups, file backups, and disaster recovery procedures.

## 🎯 Backup Strategy

### Backup Types
1. **Daily Backups**: Full database backup, retained for 7 days
2. **Weekly Backups**: Full system backup, retained for 4 weeks  
3. **Monthly Backups**: Complete backup with logs, retained for 12 months

### What Gets Backed Up
- **PostgreSQL Database**: All tables, indexes, and data
- **Configuration Files**: .env.production, nginx.conf, docker-compose.yml
- **SSL Certificates**: Certificate and key files
- **Application Logs**: System and error logs
- **User Uploads**: CSV files and analysis results

## 🔧 Backup System Components

### Scripts
- `backup_system.ps1` - Main backup script
- `setup_backup_schedule.ps1` - Windows Task Scheduler setup
- `restore_system.ps1` - Disaster recovery script

### Directory Structure
```
backups/
├── daily/          # Daily backups (7 days retention)
├── weekly/         # Weekly backups (4 weeks retention)
├── monthly/        # Monthly backups (12 months retention)
└── logs/           # Backup operation logs
```

## 📋 Manual Backup Operations

### Create Manual Backup
```powershell
# Full database backup
.\backup_system.ps1

# Test backup system
.\backup_system.ps1 -Test

# Backup with cloud upload
.\backup_system.ps1 -CloudUpload
```

### Restore from Backup
```powershell
# List available backups
Get-ChildItem backups\daily\*.sql | Sort-Object LastWriteTime -Descending

# Restore from specific backup
.\backup_system.ps1 -Restore -RestoreFile "backups\daily\backup_20251012.sql"

# Restore latest backup
.\restore_system.ps1 -Latest
```

## ⏰ Automated Backup Schedule

### Windows Task Scheduler Setup
```powershell
# Create automated backup tasks
.\setup_backup_schedule.ps1

# Verify tasks were created
schtasks /query /tn "FreeMobilaChat*"

# Remove backup tasks
.\setup_backup_schedule.ps1 -Remove
```

### Backup Schedule
- **Daily**: 2:00 AM every day
- **Weekly**: 3:00 AM every Sunday
- **Monthly**: 4:00 AM on the 1st of each month

### Task Configuration
```xml
<!-- Daily Backup Task -->
<Task>
    <Triggers>
        <CalendarTrigger>
            <StartBoundary>2025-10-12T02:00:00</StartBoundary>
            <ScheduleByDay>
                <DaysInterval>1</DaysInterval>
            </ScheduleByDay>
        </CalendarTrigger>
    </Triggers>
    <Actions>
        <Exec>
            <Command>powershell.exe</Command>
            <Arguments>-ExecutionPolicy Bypass -File "backup_system.ps1" -BackupType daily</Arguments>
            <WorkingDirectory>C:\FreeMobilaChat</WorkingDirectory>
        </Exec>
    </Actions>
</Task>
```

## ☁️ Cloud Backup Integration

### AWS S3 Configuration
```powershell
# Configure AWS credentials
aws configure set aws_access_key_id YOUR_ACCESS_KEY
aws configure set aws_secret_access_key YOUR_SECRET_KEY
aws configure set default.region us-east-1

# Upload backup to S3
.\backup_system.ps1 -CloudUpload -S3Bucket "freemobilachat-backups"
```

### Azure Blob Storage
```powershell
# Install Azure CLI
winget install Microsoft.AzureCLI

# Login to Azure
az login

# Upload backup
az storage blob upload --account-name "backupstorage" --container-name "backups" --file "backup.sql"
```

## 🔍 Backup Verification

### Automated Verification
```powershell
# Test backup integrity
.\backup_system.ps1 -Verify -BackupFile "backups\daily\backup_20251012.sql"

# Verify all recent backups
Get-ChildItem backups\daily\*.sql | ForEach-Object { 
    Write-Host "Verifying: $($_.Name)"
    .\backup_system.ps1 -Verify -BackupFile $_.FullName
}
```

### Manual Verification
```sql
-- Connect to test database
psql -h localhost -p 5433 -U mobilachat_user -d test_restore

-- Check table counts
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes
FROM pg_stat_user_tables;

-- Verify data integrity
SELECT COUNT(*) FROM tweets;
SELECT COUNT(*) FROM analysis_results;
SELECT COUNT(*) FROM users;
```

## 🚨 Disaster Recovery Procedures

### Complete System Recovery
1. **Prepare New Server**
   ```bash
   # Install Docker and Docker Compose
   # Clone FreeMobilaChat repository
   # Copy configuration files from backup
   ```

2. **Restore Database**
   ```powershell
   # Start PostgreSQL container
   docker-compose up -d postgres
   
   # Restore from latest backup
   .\restore_system.ps1 -Latest -DatabaseOnly
   ```

3. **Restore Application**
   ```powershell
   # Copy configuration files
   Copy-Item "backups\config\*.env" -Destination "."
   Copy-Item "backups\config\nginx.conf" -Destination "."
   
   # Start all services
   docker-compose up -d
   ```

4. **Verify Recovery**
   ```powershell
   # Test application endpoints
   Invoke-WebRequest "http://localhost:8080/api/health"
   
   # Verify database connectivity
   .\backup_system.ps1 -Test
   ```

### Partial Recovery Scenarios

#### Database Corruption
```powershell
# Stop application
docker-compose stop backend frontend

# Restore database only
.\restore_system.ps1 -DatabaseOnly -BackupFile "backups\daily\latest.sql"

# Restart application
docker-compose start backend frontend
```

#### Configuration Loss
```powershell
# Restore configuration files
Copy-Item "backups\config\.env.production" -Destination "."
Copy-Item "backups\config\nginx.conf" -Destination "."

# Restart services
docker-compose restart
```

## 📊 Backup Monitoring

### Log Analysis
```powershell
# View backup logs
Get-Content "backups\logs\backup.log" -Tail 50

# Check for errors
Get-Content "backups\logs\backup.log" | Select-String "ERROR|FAILED"

# Backup statistics
Get-ChildItem backups\daily\*.sql | Measure-Object -Property Length -Sum
```

### Health Checks
```powershell
# Check backup freshness
$latestBackup = Get-ChildItem backups\daily\*.sql | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$age = (Get-Date) - $latestBackup.LastWriteTime
Write-Host "Latest backup is $($age.TotalHours) hours old"

# Verify backup sizes
Get-ChildItem backups\*\*.sql | ForEach-Object {
    $sizeMB = [math]::Round($_.Length / 1MB, 2)
    Write-Host "$($_.Name): $sizeMB MB"
}
```

## 🔒 Security Considerations

### Backup Encryption
```powershell
# Encrypt backup files
$password = ConvertTo-SecureString "YourStrongPassword" -AsPlainText -Force
Compress-Archive -Path "backup.sql" -DestinationPath "backup.zip" -CompressionLevel Optimal
```

### Access Control
- Store backups in secure locations
- Use encrypted cloud storage
- Implement access logging
- Regular security audits

### Retention Policies
- Daily: 7 days (automatic cleanup)
- Weekly: 4 weeks (automatic cleanup)
- Monthly: 12 months (manual review)
- Archive: Long-term storage for compliance

## 📋 Production Checklist

- [ ] Backup scripts tested and working
- [ ] Windows Task Scheduler tasks created
- [ ] Backup directories created with proper permissions
- [ ] Cloud storage configured (optional)
- [ ] Backup verification procedures tested
- [ ] Disaster recovery procedures documented
- [ ] Monitoring and alerting configured
- [ ] Retention policies implemented
- [ ] Security measures in place
- [ ] Team trained on backup/restore procedures

## 🔧 Troubleshooting

### Common Issues

#### Backup Script Fails
```powershell
# Check database connectivity
docker exec freemobilachat_postgres pg_isready

# Verify credentials
$env:PGPASSWORD = "SecureProductionPassword2025"
pg_dump -h localhost -p 5433 -U mobilachat_user -d freemobilachat_prod --version
```

#### Task Scheduler Issues
```powershell
# Check task status
schtasks /query /tn "FreeMobilaChat-Daily-Backup" /fo LIST

# View task history
Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-TaskScheduler/Operational'; ID=201}
```

#### Storage Space Issues
```powershell
# Check disk space
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, @{Name="Size(GB)";Expression={[math]::Round($_.Size/1GB,2)}}, @{Name="FreeSpace(GB)";Expression={[math]::Round($_.FreeSpace/1GB,2)}}

# Clean old backups
.\cleanup_old_backups.ps1 -DaysToKeep 7
```

---
**Status**: Backup system ready for production
**Next Steps**: Set up automated backup schedule
**Last Updated**: October 12, 2025
