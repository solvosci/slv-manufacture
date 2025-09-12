1. Navigate to *Equipment*, by *Weight Management* or *Maintenance*.

2. Select one equipment.

3. Configure the directory paths:

    - Input Folder: Path where XML files to be processed will be placed.
    - Processed Folder: Path where XML files will be moved after successful import.

4. XML files that fail to import due to validation or processing errors will remain in the Input Folder.
Detailed error logs are generated and accessible under XML Import Errors for review and troubleshooting.

5. If enabled, the system can connect to an external FTP server to retrieve and process XML files. The following fields are required for a successful connection:

    - Host (IP or URL) – Address of the FTP server
    - Port – Usually 21 (default for FTP)
    - Username – FTP login user
    - Password – FTP login password

The optional Folder field specifies the remote directory where the XML files are located. If not provided, the connection will use the default root directory of the FTP user.

6. The process is automated via a scheduled cron job configured to run hourly by default.

7. You can optionally configure a notification partner in *Weight Management* > *Configuration* > *Settings*.
That partner will receive email alerts for any import errors detected during cron execution.

8. You can define the retention period (in days) for processed files at the equipment level.
By default, files are kept for 90 days. The cleanup runs daily via a scheduled cron job.
If the value is set to 0, files will be kept indefinitely.
