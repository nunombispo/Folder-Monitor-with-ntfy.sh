#!/usr/bin/env python3
"""
Folder Monitor with ntfy.sh Notifications

This script monitors a folder for file changes and sends different types of
notifications via ntfy.sh when files are created, modified, or deleted.
"""

import json
import time
import argparse
import logging
import os
import sys
from datetime import datetime

import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


class FileChangeHandler(FileSystemEventHandler):
    """Handle file system events and send notifications"""
    
    def __init__(self, topic, include_extensions=None, exclude_directories=True):
        """
        Initialize the handler
        
        Args:
            topic (str): ntfy topic to send notifications to
            include_extensions (list, optional): List of file extensions to monitor (e.g. ['.txt', '.pdf'])
            exclude_directories (bool): Whether to exclude directory events
        """
        self.topic = topic
        self.include_extensions = include_extensions
        self.exclude_directories = exclude_directories
        
        # Send a notification that monitoring has started
        self.send_notification(
            "Started monitoring folder for changes",
            title="Folder Monitoring Started",
            priority=3,  # default priority
            tags="rocket"
        )
        logger.info(f"Started monitoring. Notifications will be sent to topic: {topic}")
        
        if include_extensions:
            logger.info(f"Monitoring only these extensions: {', '.join(include_extensions)}")
    
    def should_process_event(self, event):
        """Check if the event should be processed based on configuration"""
        # Skip directory events if configured to do so
        if self.exclude_directories and event.is_directory:
            return False
        
        # If extensions filter is set, check the file extension
        if self.include_extensions and not event.is_directory:
            _, ext = os.path.splitext(event.src_path)
            if ext.lower() not in self.include_extensions:
                return False
                
        return True
    
    def on_created(self, event):
        """Handle file/directory creation events"""
        if not self.should_process_event(event):
            return
            
        path = event.src_path
        filename = os.path.basename(path)
        file_size = self._get_file_size(path)
        
        logger.info(f"Created: {path}")
        
        # Send notification for file creation
        self.send_notification(
            f"File created: {filename}\nLocation: {path}\nSize: {file_size}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            title="File Created",
            priority=3,  # default priority
            tags="file_folder,new"
        )
    
    def on_modified(self, event):
        """Handle file/directory modification events"""
        if not self.should_process_event(event):
            return
            
        path = event.src_path
        filename = os.path.basename(path)
        file_size = self._get_file_size(path)
        
        logger.info(f"Modified: {path}")
        
        # Send notification for file modification
        self.send_notification(
            f"File modified: {filename}\nLocation: {path}\nSize: {file_size}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            title="File Modified",
            priority=2,  # low priority
            tags="pencil"
        )
    
    def on_deleted(self, event):
        """Handle file/directory deletion events"""
        if not self.should_process_event(event):
            return
            
        path = event.src_path
        filename = os.path.basename(path)
        
        logger.info(f"Deleted: {path}")
        
        # Send notification for file deletion with high priority
        self.send_notification(
            f"File deleted: {filename}\nLocation: {path}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            title="File Deleted",
            priority=4,  # high priority
            tags="wastebasket,warning"
        )
    
    def on_moved(self, event):
        """Handle file/directory move events"""
        if not self.should_process_event(event):
            return
            
        src_path = event.src_path
        dest_path = event.dest_path
        src_filename = os.path.basename(src_path)
        dest_filename = os.path.basename(dest_path)
        
        logger.info(f"Moved: {src_path} -> {dest_path}")
        
        # Send notification for file move
        self.send_notification(
            f"File moved:\nFrom: {src_path}\nTo: {dest_path}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            title=f"File Renamed: {src_filename} → {dest_filename}" if src_path.rsplit('/', 1)[0] == dest_path.rsplit('/', 1)[0] else "File Moved",
            priority=3,  # default priority
            tags="arrow_right"
        )
    
    def _get_file_size(self, path):
        """Get human-readable file size"""
        try:
            if os.path.isfile(path):
                size_bytes = os.path.getsize(path)
                for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                    if size_bytes < 1024 or unit == 'TB':
                        return f"{size_bytes:.2f} {unit}"
                    size_bytes /= 1024
            return "N/A (directory)"
        except Exception as e:
            logger.error(f"Error getting file size: {str(e)}")
            return "Unknown"
    
    def send_notification(self, message, title=None, priority=None, tags=None, 
                         click=None, attach=None, actions=None):
        """
        Send a notification to ntfy.sh
        
        Args:
            message (str): The notification message
            title (str, optional): Notification title
            priority (str or int, optional): Priority (5=urgent, 4=high, 3=default, 2=low, 1=min)
            tags (str, optional): Comma-separated list of tags/emojis
            click (str, optional): URL to open when notification is clicked
            attach (str, optional): URL of an attachment to include
            actions (str, optional): Notification action buttons
        """
        url = "https://ntfy.sh"
        
        # Create JSON payload
        payload = {
            "topic": self.topic,
            "message": message,
        }
        
        if title:
            payload["title"] = title
        if priority:
            # Convert string priority to numeric priority
            if isinstance(priority, str):
                priority_map = {
                    "urgent": 5,
                    "high": 4,
                    "default": 3,
                    "low": 2,
                    "min": 1
                }
                if priority in priority_map:
                    payload["priority"] = priority_map[priority]
            else:
                payload["priority"] = priority
        if tags:
            payload["tags"] = [tags]
        if click:
            payload["click"] = click
        if attach:
            payload["attach"] = attach
        if actions:
            payload["actions"] = actions
        
        try:
            # Send JSON payload in the request body
            response = requests.post(
                url, 
                data=json.dumps(payload),
            )
            if response.status_code == 200:
                logger.debug(f"Notification sent: {title}")
            else:
                logger.error(f"Failed to send notification: {response.status_code}")
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="Monitor a folder and send ntfy.sh notifications on file changes")
    parser.add_argument("--path", required=True, help="Path to the folder to monitor")
    parser.add_argument("--topic", required=True, help="ntfy.sh topic for notifications")
    parser.add_argument("--extensions", help="Comma-separated list of file extensions to monitor (e.g., .txt,.pdf,.docx)")
    parser.add_argument("--include-directories", action="store_true", help="Include directory events in notifications")
    parser.add_argument("--recursive", action="store_true", help="Watch subdirectories recursively")
    
    args = parser.parse_args()
    
    # Check if the path exists
    if not os.path.exists(args.path):
        logger.error(f"The specified path does not exist: {args.path}")
        sys.exit(1)
    
    # Process file extensions if provided
    include_extensions = None
    if args.extensions:
        include_extensions = [ext.strip().lower() if ext.strip().startswith('.') else f'.{ext.strip().lower()}' 
                            for ext in args.extensions.split(',')]
    
    # Create the event handler and observer
    event_handler = FileChangeHandler(
        args.topic,
        include_extensions=include_extensions,
        exclude_directories=not args.include_directories
    )
    
    observer = Observer()
    observer.schedule(event_handler, args.path, recursive=args.recursive)
    observer.start()
    
    logger.info(f"Monitoring folder: {os.path.abspath(args.path)} (recursive: {args.recursive})")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
        
        # Send notification that monitoring has stopped
        event_handler.send_notification(
            "Folder monitoring stopped by user",
            title="Monitoring Stopped",
            priority=3,  # default priority
            tags="stop_sign"
        )
        
        observer.stop()
    
    observer.join()


if __name__ == "__main__":
    main() 