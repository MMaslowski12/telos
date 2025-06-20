"""
Setup module for Telos - handles Google Sheets integration and environment setup
"""

import datetime
from .gsheet_setup import setup_gsheet_connection
from environment.environment import Environment

def get_worksheet_name():
    """Generate a worksheet name that mirrors the plane naming convention."""
    now = datetime.datetime.now()
    timestamp = now.strftime('%d-%m-%H:%M')
    return f"plane_{timestamp}"

def setup_telos():
    """
    Complete setup for Telos including Google Sheets integration.
    
    Returns:
        tuple: (Environment object, bool success) - Environment if successful, None if failed
    """
    # Configuration
    CREDENTIALS_PATH = "setup/service-account-credentials.json"
    SHEET_NAME = "syf"  # Keep the existing sheet name
    WORKSHEET_NAME = get_worksheet_name()
    
    try:
        print("Connecting to Google Sheets...")
        client = setup_gsheet_connection(CREDENTIALS_PATH, SHEET_NAME)
        
        # Get the spreadsheet and create/find the worksheet
        spreadsheet = client.open(SHEET_NAME)
        
        # Try to get existing worksheet, create if it doesn't exist
        try:
            worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
            print(f"✓ Found existing worksheet: {WORKSHEET_NAME}")
        except:
            # Copy from Template worksheet
            try:
                template_worksheet = spreadsheet.worksheet("Template")
                worksheet = template_worksheet.duplicate(new_sheet_name=WORKSHEET_NAME)
                print(f"✓ Created new worksheet from Template: {WORKSHEET_NAME}")
            except:
                # If Template doesn't exist, create a blank worksheet
                worksheet = spreadsheet.add_worksheet(title=WORKSHEET_NAME, rows=1000, cols=26)
                print(f"⚠ Template worksheet not found, created blank worksheet: {WORKSHEET_NAME}")
        
        print(f"✓ Connected to sheet: {SHEET_NAME} - worksheet: {WORKSHEET_NAME}")
        
        # Create environment instance
        print("Creating aircraft environment...")
        env = Environment(worksheet=worksheet)
        print("✓ Environment created successfully")
        
        # Load data from sheet
        print("Loading data from Google Sheets...")
        env.from_gsheet(worksheet)
        print("✓ Data loaded from sheet")
        
        # Update all calculations
        print("Running calculations...")
        env.update_all()
        print("✓ Calculations completed")
        
        # Push results back to sheet
        print("Pushing results to Google Sheets...")
        env.push_to_gsheet(worksheet)
        print("✓ Results pushed to sheet")
        
        # Validate everything
        print("Validating results...")
        if env.validate():
            print("✓ All validations passed")
        else:
            print("⚠ Some validations failed - check warnings above")
            
        print("\n🎉 Google Sheets integration is working!")
        return env, True
        
    except Exception as e:
        print(f"❌ Google Sheets Error: {str(e)}")
        print("Continuing with local setup...")
        return None, False 