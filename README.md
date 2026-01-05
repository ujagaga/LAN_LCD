# Lan LCD

Using Orange Pi One or Zero SBC, 2.4" LCD and an Arduino UNO, I built a networked status display. It can be used for monitoring services.

The idea is to have a Python HTTP server to which you can send any text using either HTTP GET or POST request.
For POST request you can send:

        {"txt":"Some text to display", "fg": "<font HEX color or a predefined one>", "bg":"<Background color>", "size": "<text size>"}

The same for GET request is sent using query parameters:

        /set/?txt=Hello&fg=WHITE&bg=BLUE&size=3

If you send a json that is missing any of the JSON keys, the Arduino UNO will just use the latest it has remembered.

After I connect the device to network, it will display the IP address and then wait for the first message to show.
Each new message cleares the old one.

## NOTE:
There are now cheap ESP32 based LCD displays, but I wanted a linux server so I can add custom automation services. 
Also I had this hardware laying around, not usefull for anything else, so I decided to do something usefull with it. 

## Status
Usable. Missing IP address detection and displaying it at startup.