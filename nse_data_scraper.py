#!/usr/bin/env python3
"""
NSE Data Scraper for Bulk Deals
Real-time scraper to fetch bulk and block deals data from NSE India website
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import time
from typing import Dict, List, Optional
import logging

class NSEDataScraper:
    """
    Scraper to fetch real bulk deals data from NSE India
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.nseindia.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        self.session.headers.update(self.headers)
        
        # Initialize session with cookies
        self._init_session()
    
    def _init_session(self):
        """Initialize session and get required cookies"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✓ Session initialized successfully")
            else:
                print(f"⚠ Warning: Session initialization returned status {response.status_code}")
        except Exception as e:
            print(f"✗ Error initializing session: {e}")
    
    def fetch_bulk_deals(self, date: str) -> pd.DataFrame:
        """
        Fetch bulk deals data for a specific date
        
        Args:
            date: Date in DD-MM-YYYY format
            
        Returns:
            DataFrame with bulk deals data
        """
        try:
            # Convert date format
            date_obj = datetime.strptime(date, "%d-%m-%Y")
            formatted_date = date_obj.strftime("%d-%m-%Y")
            
            # API endpoint for bulk deals
            url = f"{self.base_url}/api/reports-bulk-deals?date={formatted_date}"
            
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and data['data']:
                    df = pd.DataFrame(data['data'])
                    df['trade_date'] = date
                    print(f"✓ Fetched {len(df)} bulk deals for {date}")
                    return df
                else:
                    print(f"⚠ No bulk deals data found for {date}")
                    return pd.DataFrame()
            else:
                print(f"✗ Error fetching data for {date}: Status {response.status_code}")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"✗ Error fetching bulk deals for {date}: {e}")
            return pd.DataFrame()
    
    def fetch_block_deals(self, date: str) -> pd.DataFrame:
        """
        Fetch block deals data for a specific date
        
        Args:
            date: Date in DD-MM-YYYY format
            
        Returns:
            DataFrame with block deals data
        """
        try:
            # Convert date format
            date_obj = datetime.strptime(date, "%d-%m-%Y")
            formatted_date = date_obj.strftime("%d-%m-%Y")
            
            # API endpoint for block deals
            url = f"{self.base_url}/api/reports-block-deals?date={formatted_date}"
            
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and data['data']:
                    df = pd.DataFrame(data['data'])
                    df['trade_date'] = date
                    print(f"✓ Fetched {len(df)} block deals for {date}")
                    return df
                else:
                    print(f"⚠ No block deals data found for {date}")
                    return pd.DataFrame()
            else:
                print(f"✗ Error fetching data for {date}: Status {response.status_code}")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"✗ Error fetching block deals for {date}: {e}")
            return pd.DataFrame()
    
    def fetch_date_range(self, start_date: str, end_date: str, deal_type: str = "bulk") -> pd.DataFrame:
        """
        Fetch bulk/block deals data for a date range
        
        Args:
            start_date: Start date in DD-MM-YYYY format
            end_date: End date in DD-MM-YYYY format
            deal_type: "bulk" or "block"
            
        Returns:
            Combined DataFrame with all deals data
        """
        start_dt = datetime.strptime(start_date, "%d-%m-%Y")
        end_dt = datetime.strptime(end_date, "%d-%m-%Y")
        
        all_data = []
        current_date = start_dt
        
        print(f"\nFetching {deal_type} deals from {start_date} to {end_date}")
        print("-" * 50)
        
        while current_date <= end_dt:
            # Skip weekends
            if current_date.weekday() < 5:  # Monday = 0, Sunday = 6
                date_str = current_date.strftime("%d-%m-%Y")
                
                if deal_type == "bulk":
                    day_data = self.fetch_bulk_deals(date_str)
                else:
                    day_data = self.fetch_block_deals(date_str)
                
                if not day_data.empty:
                    all_data.append(day_data)
                
                # Rate limiting
                time.sleep(0.5)
            
            current_date += timedelta(days=1)
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            print(f"\n✓ Total {deal_type} deals fetched: {len(combined_df)}")
            return combined_df
        else:
            print(f"\n⚠ No {deal_type} deals data found for the specified range")
            return pd.DataFrame()
    
    def save_to_csv(self, df: pd.DataFrame, filename: str):
        """Save DataFrame to CSV file"""
        try:
            df.to_csv(filename, index=False)
            print(f"✓ Data saved to {filename}")
        except Exception as e:
            print(f"✗ Error saving to CSV: {e}")
    
    def get_recent_bulk_deals(self, days: int = 30) -> pd.DataFrame:
        """
        Get bulk deals for the last N trading days
        
        Args:
            days: Number of days to look back
            
        Returns:
            DataFrame with recent bulk deals
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Format dates
        start_str = start_date.strftime("%d-%m-%Y")
        end_str = end_date.strftime("%d-%m-%Y")
        
        return self.fetch_date_range(start_str, end_str, "bulk")

def main():
    """
    Example usage of the NSE Data Scraper
    """
    print("NSE Bulk Deals Data Scraper")
    print("=" * 50)
    
    scraper = NSEDataScraper()
    
    # Example 1: Get recent bulk deals (last 7 days)
    print("\n1. Fetching recent bulk deals (last 7 days)...")
    recent_bulk = scraper.get_recent_bulk_deals(days=7)
    
    if not recent_bulk.empty:
        print("\nRecent Bulk Deals Sample:")
        print(recent_bulk.head())
        scraper.save_to_csv(recent_bulk, "recent_bulk_deals.csv")
    
    # Example 2: Get specific date range
    print("\n2. Fetching bulk deals for specific date range...")
    start_date = "01-01-2024"  # DD-MM-YYYY
    end_date = "31-01-2024"    # DD-MM-YYYY
    
    bulk_deals = scraper.fetch_date_range(start_date, end_date, "bulk")
    
    if not bulk_deals.empty:
        print(f"\nBulk Deals Summary ({start_date} to {end_date}):")
        print(f"Total deals: {len(bulk_deals)}")
        print(f"Unique stocks: {bulk_deals['symbol'].nunique() if 'symbol' in bulk_deals.columns else 'N/A'}")
        print(f"Date range: {bulk_deals['trade_date'].min()} to {bulk_deals['trade_date'].max()}")
        
        scraper.save_to_csv(bulk_deals, f"bulk_deals_{start_date.replace('-', '')}_to_{end_date.replace('-', '')}.csv")
    
    # Example 3: Get block deals
    print("\n3. Fetching recent block deals...")
    block_deals = scraper.fetch_date_range(start_date, end_date, "block")
    
    if not block_deals.empty:
        print(f"\nBlock Deals Summary:")
        print(f"Total deals: {len(block_deals)}")
        scraper.save_to_csv(block_deals, f"block_deals_{start_date.replace('-', '')}_to_{end_date.replace('-', '')}.csv")

if __name__ == "__main__":
    main()