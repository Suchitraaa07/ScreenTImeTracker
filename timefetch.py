import pygetwindow as gw
from datetime import datetime 
import time

def fetch_window_times(duration):

    start = time.time()
    start_time = datetime.now()
    currwindow = None
    window = None
    windowrecord = []

    while time.time() - start < duration:
        window = gw.getActiveWindow()
        if window is None:
                time.sleep(0.5)
                continue
        
        if currwindow is None:
            start_time = datetime.now()
            currwindow = window
            time.sleep(3)

        elif currwindow.title == window.title:
             time.sleep(1)
             continue

        else:
            end_time = datetime.now()
            duration_seconds = (end_time - start_time).total_seconds()
            if duration_seconds >3600:
                duration_seconds = duration_seconds/3600
            windowrecord.append( ( currwindow.title, start_time, end_time, duration_seconds) )
            start_time = datetime.now()
            currwindow = window
            time.sleep(3)

    if currwindow is not None:
        end_time = datetime.now()
        duration_seconds = (end_time - start_time).total_seconds()
        if duration_seconds >3600:
                duration_seconds = duration_seconds/3600
        windowrecord.append(
            (currwindow.title, start_time, end_time, duration_seconds)
        )

    return windowrecord