'''
xflrpy/xflrpy.app/Contents/MacOS/xflrpy
'''

from tools import ToolManager
from utils import get_next_id
from delphi import chat_loop

project_name = "epstein_didnt_kill_himself.xfl"
project_path = "xflrpy/projects/"
id = get_next_id()
plane_name = f"plane_{id}"
analysis_name = f"analysis_{id}"

if __name__ == "__main__":
    tm = ToolManager(project_path, project_name, plane_name)
    plane, plane_data = tm.setup_airplane()
    
    print("Plane name: ", plane_name)
    chat_loop(tm)



'''
TODO

Transfer the excel to python
Set up the first prompt (make lift positive)

THEN:
Install and run the xflrpy 0.48
Do the transcript of the conversation


BACKLOG:
More degrees of freedom: change the center of mass, change airfoils, add more sections, etc. (consult Paweł and add debug_info with feature requests from an LLM)


Can you change the chord of the first sector of the wing to 2?
'''