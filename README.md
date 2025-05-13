# Folder Monitor with ntfy.sh Notifications

This Python script monitors a folder for file changes and sends push notifications via [ntfy.sh](https://ntfy.sh) when files are created, modified, or deleted.

If these scripts were useful to you, consider donating to support the Developer Service Blog: https://buy.stripe.com/bIYdTrggi5lZamkdQW

## Features

- Real-time folder monitoring using watchdog
- Push notifications for file creation, modification, deletion, and moves
- Different notification styles and priorities based on event type
- Notifications sent as JSON payloads
- Filter monitoring by file extensions
- Recursive directory monitoring support
- Human-readable file size display
- Detailed logging

## Setup

1. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Subscribe to a topic in the ntfy.sh app:
   - Install the [ntfy app](https://ntfy.sh/app) on your phone (available for Android and iOS)
   - Or use the [web app](https://ntfy.sh/app)
   - Subscribe to a unique topic name of your choice (pick something that others won't guess)

## Usage

Basic usage:

```bash
python folder_monitor.py --path /path/to/monitor --topic your_unique_topic
```

Advanced options:

```bash
# Monitor only specific file types
python folder_monitor.py --path /path/to/monitor --topic your_unique_topic --extensions .txt,.pdf,.docx

# Include notifications for directory changes
python folder_monitor.py --path /path/to/monitor --topic your_unique_topic --include-directories

# Recursively monitor all subdirectories
python folder_monitor.py --path /path/to/monitor --topic your_unique_topic --recursive

# Combine options
python folder_monitor.py --path /path/to/monitor --topic your_unique_topic --extensions .txt,.pdf --recursive
```

## Notification Types

The script sends different types of notifications based on the file event:

1. **File Created**: Default priority (3) with "file_folder" and "new" tags
2. **File Modified**: Low priority (2) with "pencil" tag
3. **File Deleted**: High priority (4) with "wastebasket" and "warning" tags
4. **File Moved/Renamed**: Default priority (3) with "arrow_right" tag
5. **Monitoring Started**: Default priority (3) with "rocket" tag
6. **Monitoring Stopped**: Default priority (3) with "stop_sign" tag

Each notification is sent as a JSON payload that includes:

- Message content
- Event type as the title
- Appropriate priority level (numeric value)
- Relevant emoji tags
- Other metadata for the event

## Technical Details

Notifications are sent to ntfy.sh as JSON payloads with the following structure:

```json
{
  "topic": "your_topic_name",
  "message": "The notification message with details",
  "title": "Event Type",
  "priority": 3,
  "tags": ["tag1", "tag2"],
  ...other optional fields...
}
```

Priority levels are numeric values:

- 5: Urgent
- 4: High
- 3: Default
- 2: Low
- 1: Min

This format allows for clean, structured notifications that can be easily processed by automation tools.

## Security Note

Topics are public, so choose unique topic names that others cannot guess. Anyone who knows your topic name can send notifications to it or read messages from it.

## Further Reading

For more information, see the [ntfy.sh documentation](https://docs.ntfy.sh/).
