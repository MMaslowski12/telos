import json
import os
import datetime

def get_next_id():
    now = datetime.datetime.now()
    return now.strftime('%d-%m-%H:%M')
