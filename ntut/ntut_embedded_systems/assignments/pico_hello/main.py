# NTUT Embedded Systems Class
#
# PURIT HONGJIRAKUL (114998411)
# KU YUN HSIANG (113598061)
# MILAN ESSER (114012022)
# WEN LI SUN (113598059)

import network
import socket
import time
import random
from machine import Pin

led = Pin('LED', Pin.OUT)

ssid = 'IcePick15'
password = 'qwertyasdf'

# HTML template
def webpage(rand_num, state, hello_msg):
    html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pico Web Server</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{
                    font-family: Consolas, sans-serif;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f0f0f0;
                }}
            </style>
        </head>
        <body>
            <h1>NTUT Embedded Systems</h1>
            <h1>Raspberry Pi Pico W "Hello" Assignment</h1>
            <br>
            <h2>Hello Message</h2>
            <form action="./hello">
                <input type="submit" value="Say Hello!" />
            </form>
            <p>{hello_msg}</p>
            <br>
            <h2>Led Control</h2>
            <form action="./lighton">
                <input type="submit" value="Light on" />
            </form>
            <br>
            <form action="./lightoff">
                <input type="submit" value="Light off" />
            </form>
            <p>LED state: {state}</p>
            <br>
            <h2>Random Number Generator</h2>
            <form action="./random">
                <input type="submit" value="Generate" />
            </form>
            <p>Number: {rand_num}</p>
            <br>
            <h2>Created by:</h2>
            <ul>
                <li>PURIT HONGJIRAKUL (114998411)</li>
                <li>KU YUN HSIANG (113598061)</li>
                <li>MILAN ESSER (114012022)</li>
                <li>WEN LI SUN (113598059)</li>
            </ul>
        </body>
        </html>
        """
    return str(html)

# WLAN conn
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# WiFi conn
connection_timeout = 10
while connection_timeout > 0:
    if wlan.status() >= 3:
        break
    connection_timeout -= 1
    print('Waiting for Wi-Fi connection...')
    time.sleep(1)

# check successful connection
if wlan.status() != 3:
    raise RuntimeError('Failed to establish a network connection')
else:
    print('Connection successful!')
    network_info = wlan.ifconfig()
    print('IP address:', network_info[0])

# set up socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen()

print('Listening on', addr)

# init variables
state = "OFF"
hello_msg = ""
rand_num = ""

# main loop to listen for connections
while True:
    try:
        conn, addr = s.accept()
        print('Got a connection from', addr)
        
        # receive and parse request
        request = conn.recv(1024)
        request = str(request)
        print('Request content = %s' % request)

        try:
            request = request.split()[1]
            print('Request:', request)
        except IndexError:
            pass
        
        if request == '/lighton?':
            print("LED on")
            led.value(1)
            state = "ON"
        elif request == '/lightoff?':
            led.value(0)
            state = 'OFF'
        elif request == '/hello?':
            hello_msg = "Hello from Raspberry Pi Pico 2 W!"
        elif request == '/random?':
            rand_num = random.randint(1, 100)

        # generate HTML response & send
        response = webpage(rand_num, state, hello_msg)  
        conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        conn.send(response)
        conn.close()

    except OSError as e:
        conn.close()
        print('Connection closed')