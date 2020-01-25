"""
MIT License

Copyright (c) [2020] [Daniel B.]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import requests
import time
import board
import neopixel


pixel_pin = board.D18     # Data Pin Raspberry Pi
num_pixels = 60           # Number of leds
ORDER = neopixel.GRB      # Color order of the strip

# Configuring the strip
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.6, auto_write=False, pixel_order=ORDER)

#URL of the printers API's
url = "http://add_the_ip_of_the_octoprint_server_here:5000/api/job"
url1 = "http://add_the_ip_of_the_octoprint_server_here:5000/api/printer"

payload = {}
headers = {'X-Api-Key': 'add_your_API_key_here'}     # API Key


def wheel(pos):
  if pos < 0 or pos > 255:
    r = g = b = 0
  elif pos < 85:
    r = int(pos * 3)
    g = int(255 - pos*3)
    b = 0
  elif pos < 170:
    pos -= 85
    r = int(255 - pos*3)
    g = 0
    b = int(pos*3)
  else:
    pos -= 170
    r = 0
    g = int(pos*3)
    b = int(255 - pos*3)
  return (r, g, b) if ORDER == neopixel.RGB or ORDER == neopixel.GRB else (r, g, b, 0)


# Function for rainbow light
def rainbow_cycle(wait):
  for j in range(255):
    for i in range(num_pixels):
      pixel_index = (i * 256 // num_pixels) + j
      pixels[i] = wheel(pixel_index & 255)
    pixels.show()
    time.sleep(wait)


# Main loop
while True:

  # Performing the requests
  response = requests.request("GET", url, headers=headers, data = payload)
  response1 = requests.request("GET", url1, headers=headers, data = payload)

  # Converting the responses in .json files
  data = response.json()
  data1 = response1.json()

  # Reading data out of the .json Files
  progress = data['progress']['completion']
  print_time = data['progress']['printTime']
  print_time_left = data['progress']['printTimeLeft']

  printing = data1['state']['flags']['printing']
  ready = data1['state']['flags']['ready']
  error = data1['state']['flags']['error']
  paused = data1['state']['flags']['paused']
  operational = data1['state']['flags']['operational']

  bed_actuall = data1['temperature']['bed']['actual']
  bed_target = data1['temperature']['bed']['target']
  tool_actuall = data1['temperature']['tool0']['actual']
  tool_target = data1['temperature']['tool0']['target']


  # Converting the print times from seconds to minutes
  if print_time is not None:
    print_time = print_time / 60
    
  if print_time_left is not None:
    print_time_left = print_time_left / 60

  # Converting the progress to a specific led
  if progress is not None:
    led = (num_pixels / 100) * progress - 1
    led = round(led)
    if led < 0:
      led = 0


  # Printing out some informations
  print("Printing progress:",progress)
  print("Time printed:",print_time)
  print("Time left to finish:",print_time_left)
  print("Printing:",printing)
  print("Printer ready:",ready)
  print("Printer error:",error)
  print("Printer paused:",paused)
  print("Printer operational:",operational)
  print("Heatbed temperature:",bed_actuall)
  print("Target heatbed temperature:",bed_target)
  print("Extruder temperature:",tool_actuall)
  print("Target temperature extruder:",tool_target)
  print("LED:",led)
  print("")
  print("")

  pixels.fill((0, 0, 0))

  # Setting all leds to white
  if bed_target != 0 or tool_target != 0 or printing == True:
    pixels.fill((255, 255, 255))

  # Error state: Red flashing light for 10s
  if error == True:
    for i in range(50):
      pixels.fill((255, 0, 0))
      pixels.show()
      time.sleep(0.1)
      pixels.fill((0, 0, 0))
      pixels.show()
      time.sleep(0.1)
    

  # Paused state: Purple light
  if paused == True:
    pixels.fill((180, 0, 250))
    

  # Heating state: Orange light
  if bed_target > 0 or tool_target > 0:
    if (bed_target - bed_actuall) > 10 or (tool_target - tool_actuall) > 10:
      pixels.fill((250, 140, 0))


  # Printing state: Indicating the progress with an single blue led
  if printing == True:
    pixels[led] = (0, 0, 255)
    printed = 1


  # Finished state: Rainbow light
  if printing == False and progress == 100 and printed == 1:
    for i in range(30):
      rainbow_cycle(0.001)


  if printing == False and progress == 100:
    printed = 0


  pixels.show()   # Address the led strip
  time.sleep(1)   # Wait for 1s befor repeat