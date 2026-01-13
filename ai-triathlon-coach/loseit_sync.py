import logging
from playwright.sync_api import sync_playwright
import os
import time
import pandas as pd
from datetime import datetime, date, timedelta

logger = logging.getLogger(__name__)

class LoseItSync:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.download_dir = "/tmp/loseit_downloads"
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def scrape_recent_history(self):
        """
        Headless browser automation to export CSV.
        """
        data_records = []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
                context = browser.new_context(accept_downloads=True)
                page = context.new_page()

                logger.info("Navigating to LoseIt login...")
                page.goto("https://www.loseit.com/login")
                
                # Login
                page.fill('input[name="email"]', self.email)
                page.fill('input[name="password"]', self.password)
                page.click('button:has-text("Login")') # Specific selector might need adjustment based on live DOM
                
                # Wait for dashboard (implicit verification)
                page.wait_for_load_state('networkidle')
                # Navigate to the specific Insights URL for Daily Summary
                target_url = "https://www.loseit.com/#Insights:Daily%20Summary%5EDaily%20Summary"
                logger.info(f"Navigating to {target_url}...")
                page.goto(target_url)
                
                # It's a SPA, so wait for network idle or specific element
                page.wait_for_load_state('networkidle')

                logger.info("Clicking 'Export to spreadsheet'...")
                with page.expect_download() as download_info:
                    # Click the link with text "Export to spreadsheet"
                    page.click('a:has-text("Export to spreadsheet")')

                download = download_info.value
                target_path = os.path.join(self.download_dir, "loseit_export.csv")
                download.save_as(target_path)
                logger.info(f"Downloaded export to {target_path}")
                
                # Parse CSV
                if os.path.exists(target_path):
                    df = pd.read_csv(target_path)
                    # Convert to list of dicts for now. 
                    # We might need to map columns to: "Date", "Calories", "Protein", "Carbs", "Fat"
                    # Doing a loose mapping based on probable column names
                    df.columns = [c.strip().lower() for c in df.columns]
                    
                    for _, row in df.iterrows():
                        # Basic normalization (adjust based on actual CSV headers)
                        record = {
                            "Date": row.get("date", datetime.now().strftime("%Y-%m-%d")), 
                            "Calories": row.get("calories", 0),
                            "Fat": row.get("fat", 0),
                            "Protein": row.get("protein", 0),
                            "Carbohydrates": row.get("carbohydrates", 0) or row.get("carbs", 0),
                            "Note": row.get("note", "")
                        }
                        data_records.append(record)
            
            return data_records

        except Exception as e:
            logger.error(f"LoseIt scraping failed: {e}")
            return []
