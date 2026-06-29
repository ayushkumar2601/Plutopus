# Disaster Recovery Runbook - Plutopus

This guide outlines recovery instructions during system failures or data loss events.

---

## Runbook 1: Full Database Restore
If the main TimescaleDB cluster fails, execute:
1. Provision a fresh container stack or database server.
2. Transfer the backup archive files to the local target workspace.
3. Execute the restore utility script:
   ```bash
   ./scripts/restore.sh ./backups/plutopus_backup_latest.sql
   ```
4. Verify table integrity by running query validations.

---

## Runbook 2: Redpanda Topic Reinitialization
If the Redpanda messaging topic queue drops offline:
1. Verify the service is online.
2. Re-initialize topics using the startup utility:
   ```bash
   ./scripts/init-redpanda.sh
   ```

---

## Runbook 3: Offline Deployment Recovery
If the offline air-gapped host fails:
1. Extract the package file:
   ```bash
   tar -xzf plutopus-offline-bundle.tar.gz
   ```
2. Navigate to deployment, load images:
   ```bash
   docker load -i distribution/docker-images/plutopus_images.tar
   ```
3. Boot compose:
   ```bash
   docker compose up -d
   ```
