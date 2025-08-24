import pyautogui
import time
import webbrowser

# Step 1: Open browser and go to Google
webbrowser.open("https://www.google.com")
time.sleep(5)  # wait for the browser to load

# Step 2: Type the search query
pyautogui.write("South Africa vs Australia score", interval=0.1)
pyautogui.press("enter")
time.sleep(5)  # wait for results to load

# Step 3: Move to and click the first link
# Approximate coordinates (you may need to adjust based on your screen)
pyautogui.moveTo(400, 300)  # Change based on where your first result appears
pyautogui.click()
