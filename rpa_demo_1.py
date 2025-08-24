import pyautogui
import time

"""#Mouse Operations
pyautogui.click(100,100)
time.sleep(5)
pyautogui.rightClick(100,100)

time.sleep(4)
pyautogui.click(2324, 889)

pyautogui.doubleClick(100, 100)
pyautogui.drag(100,100, 200,200)
pyautogui.scrollDown(500)
"""
"""
#Keyboard Operation

time.sleep(2)
pyautogui.click(1218, 806)
#pyautogui.write("Socialeagle.ai")

pyautogui.typewrite("python rpa_demo_1.py")
#pyautogui.press('enter')

pyautogui.hotkey("ctrl", "C")
"""
#image recognition
#pip install opencv-python

location = pyautogui.locateOnScreen("copilot_img.png", confidence = 0.8)

if location:
    print("Found at:", location)
else:
    print("Image not found.")


print(pyautogui.size())
ss = pyautogui.screenshot()
ss.save("demo.png")