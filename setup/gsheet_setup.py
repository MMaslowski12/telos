"""
Google Sheets Integration Setup for Telos

This file demonstrates how to set up and use the Google Sheets integration
with the Environment class for aircraft design calculations.
"""

import os
import gspread
from google.oauth2.service_account import Credentials
from environment.environment import Environment

def setup_gsheet_connection(credentials_path: str, sheet_name: str):
    """
    Set up connection to Google Sheets.
    
    Args:
        credentials_path: Path to your service account JSON file
        sheet_name: Name of your Google Sheet
    
    Returns:
        gspread.Client: The authorized client object
    """
    # Define the scope
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # Load credentials
    credentials = Credentials.from_service_account_file(
        credentials_path, 
        scopes=scope
    )
    
    # Authorize the client
    client = gspread.authorize(credentials)
    
    # Test the connection by trying to open the spreadsheet
    try:
        spreadsheet = client.open(sheet_name)
        return client
    except gspread.SpreadsheetNotFound:
        raise ValueError(f"Spreadsheet '{sheet_name}' not found. Make sure it's shared with your service account.")
    except Exception as e:
        raise Exception(f"Error connecting to Google Sheets: {str(e)}")

def main():
    """Example usage of the Google Sheets integration."""
    
    # Configuration - update these values
    CREDENTIALS_PATH = "setup/service-account-credentials.json"
    SHEET_NAME = "syf"
    
    try:
        # Set up connection
        print("Connecting to Google Sheets...")
        client = setup_gsheet_connection(CREDENTIALS_PATH, SHEET_NAME)
        print(f"✓ Connected to sheet: {SHEET_NAME}")
        
        # Create environment instance
        print("Creating aircraft environment...")
        env = Environment(worksheet=client.open(SHEET_NAME).sheet1)
        print("✓ Environment created successfully")
        
        # Load data from sheet
        print("Loading data from Google Sheets...")
        env.from_gsheet(client.open(SHEET_NAME).sheet1)
        print("✓ Data loaded from sheet")
        
        # Update all calculations
        print("Running calculations...")
        env.update_all()
        print("✓ Calculations completed")
        
        # Push results back to sheet
        print("Pushing results to Google Sheets...")
        env.push_to_gsheet(client.open(SHEET_NAME).sheet1)
        print("✓ Results pushed to sheet")
        
        # Validate everything
        print("Validating results...")
        if env.validate():
            print("✓ All validations passed")
        else:
            print("⚠ Some validations failed - check warnings above")
            
        print("\n🎉 Google Sheets integration is working!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure your credentials JSON file path is correct")
        print("2. Ensure the Google Sheet is shared with your service account email")
        print("3. Check that the Google Sheets API is enabled in your Google Cloud project")
        print("4. Verify the sheet name matches exactly")

if __name__ == "__main__":
    main() 