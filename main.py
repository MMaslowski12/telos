'''
xflrpy/xflrpy.app/Contents/MacOS/xflrpy
/Users/mmaslowski/Documents/GitHub/Telos/xflrpy/xflrpy.app/Contents/MacOS/xflrpy
'''

from tools import ToolManager
from utils import get_next_id
from agent.agent import chat_loop
from environment.environment import Environment

project_name = "epstein_didnt_kill_himself.xfl"
project_path = "xflrpy/projects/"
id = get_next_id()
plane_name = f"plane_{id}"
analysis_name = f"analysis_{id}"

if __name__ == "__main__":
    # Setup Telos with Google Sheets integration
    
    # Method 1: Initialize with default values
    env = Environment()
    print("Environment initialized with default values:")
    print(env._get_components())
    
    # # Method 1b: Initialize with custom values
    # custom_wing_params = {
    #     'span_m': 1.5,
    #     'root_chord_m': 0.25,
    #     'tip_chord_m': 0.18,
    #     'emp_coeff': 0.12,
    #     'surface_area_m2': 0.3225
    # }
    
    # env_custom = Environment(
    #     cruise_speed_mps=15.0,
    #     wing_params=custom_wing_params
    # )
    # print("\nEnvironment initialized with custom wing parameters:")
    # print(f"Wing span: {env_custom.wing.span_m}m")
    # print(f"Wing root chord: {env_custom.wing.root_chord_m}m")
    
    # Method 2: Initialize from Google Sheets (commented out for now)
    # You would need to set up Google Sheets authentication first
    # import gspread
    # from google.oauth2.service_account import Credentials
    # 
    # # Setup Google Sheets authentication
    # scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # creds = Credentials.from_service_account_file('environment/service-account-credentials.json', scopes=scope)
    # client = gspread.authorize(creds)
    # 
    # # Open the spreadsheet (replace with your actual spreadsheet name)
    # spreadsheet = client.open('Your Spreadsheet Name')
    # worksheet = spreadsheet.get_worksheet(0)  # or specify by name
    # 
    # # Initialize environment from Google Sheets
    # env_from_sheet = Environment(from_gsheet=True, worksheet=worksheet)
    # print("Environment initialized from Google Sheets:")
    # print(env_from_sheet._get_components())
    
    # Original xflrpy setup
    tm = ToolManager(project_path, project_name, plane_name)
    plane, plane_data = tm.setup_airplane()

    # print("Plane name: ", plane_name)
    # chat_loop(tm)


'''
TODO

-> Make it work
-> Add (see_plane)
-> Talk with the bros what they'd like (force them like in April)
-> run the first loop

'''


'''
Main loop:
- Run the chat based on the plane

Tool use_gsheet (TODO: end of each call (i dont care if its redundant)): 
- Sync xflrpy to Python
- update all changes from python to excel
- Calculate in Excel & Python
- Give values back to the bot 
TODO here: craete the tool in the TM

Tool perform_analysis:
- Sync up the Environment too

add_point_masses: (TODO: subtool of modify_plane)
- Sync up the Environment too (although this is just adding stuff to the fuselage)

modify_plane
- Same thing
(TODO here: sync the xflrpy plane with my plane)

If I do everything tool side, it guarantees the bot is up to date, and what I see is what the bot sees. 


Later, to-do:
-> Get values if you change something in xflrpy yourself
-> Get the agent to work

BACKLOG:
More degrees of freedom: change the center of mass, change airfoils, add more sections, etc. (consult Paweł and add debug_info with feature requests from an LLM)
'''