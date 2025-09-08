"""
Task scheduler for automatic IPO data updates

This module provides a simple way to schedule automatic updates
using various methods like cron jobs or external schedulers.
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from django.conf import settings
from .services import finnhub_service

logger = logging.getLogger(__name__)


class IPODataScheduler:
    """Simple scheduler for IPO data updates"""
    
    def __init__(self, update_interval_hours=6):
        self.update_interval_hours = update_interval_hours
        self.last_update = None
        self.is_running = False
        self._stop_event = threading.Event()
    
    def should_update(self):
        """Check if it's time for an update"""
        if not self.last_update:
            return True
        
        time_since_update = datetime.now() - self.last_update
        return time_since_update >= timedelta(hours=self.update_interval_hours)
    
    def update_ipo_data(self):
        """Perform IPO data update"""
        try:
            logger.info("Starting scheduled IPO data update")
            stats = finnhub_service.sync_ipo_data()
            self.last_update = datetime.now()
            logger.info(f"Scheduled IPO update completed: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Error in scheduled IPO update: {str(e)}")
            return None
    
    def start_scheduler(self):
        """Start the background scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        self._stop_event.clear()
        
        def run_scheduler():
            while not self._stop_event.is_set():
                try:
                    if self.should_update():
                        self.update_ipo_data()
                    
                    # Wait for 1 hour before checking again
                    self._stop_event.wait(timeout=3600)  # 1 hour
                    
                except Exception as e:
                    logger.error(f"Error in scheduler loop: {str(e)}")
                    self._stop_event.wait(timeout=300)  # Wait 5 minutes on error
        
        thread = threading.Thread(target=run_scheduler, daemon=True)
        thread.start()
        logger.info(f"IPO data scheduler started (update interval: {self.update_interval_hours}h)")
    
    def stop_scheduler(self):
        """Stop the background scheduler"""
        if not self.is_running:
            return
        
        self._stop_event.set()
        self.is_running = False
        logger.info("IPO data scheduler stopped")


# Global scheduler instance
ipo_scheduler = IPODataScheduler(update_interval_hours=6)


def setup_cron_job():
    """
    Instructions for setting up a cron job for automatic updates
    
    Add this to your crontab (run 'crontab -e'):
    
    # Update IPO data every 6 hours
    0 */6 * * * cd /path/to/your/project && python manage.py sync_ipo_data
    
    # Or update twice daily at 9 AM and 6 PM
    0 9,18 * * * cd /path/to/your/project && python manage.py sync_ipo_data
    """
    instructions = '''
    To set up automatic IPO data updates using cron:
    
    1. Open your crontab:
       crontab -e
    
    2. Add one of these lines:
       
       # Update every 6 hours
       0 */6 * * * cd {project_path} && python manage.py sync_ipo_data
       
       # Update twice daily (9 AM and 6 PM)
       0 9,18 * * * cd {project_path} && python manage.py sync_ipo_data
       
       # Update every weekday at market open (9:15 AM IST)
       15 9 * * 1-5 cd {project_path} && python manage.py sync_ipo_data
    
    3. Save and exit
    
    Replace {project_path} with the actual path to your project directory.
    '''.format(project_path=settings.BASE_DIR)
    
    return instructions


def setup_windows_task():
    """
    Instructions for setting up Windows Task Scheduler
    """
    instructions = '''
    To set up automatic IPO data updates on Windows:
    
    1. Open Task Scheduler (taskschd.msc)
    
    2. Create Basic Task:
       - Name: "IPO Data Sync"
       - Description: "Sync IPO data from Finnhub API"
    
    3. Set Trigger:
       - Daily, every 6 hours or
       - Daily at 9:00 AM and 6:00 PM
    
    4. Set Action:
       - Program: python.exe
       - Arguments: manage.py sync_ipo_data
       - Start in: {project_path}
    
    5. Finish and test the task
    '''.format(project_path=settings.BASE_DIR)
    
    return instructions