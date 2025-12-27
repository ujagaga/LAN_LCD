# Lan LCD

Using Orange Pi One SBC and 2.4" LCD, I am building a networked status display. It can be used for monitoring services.

The idea is to have a Python HTTP server to which I can send any text using either HTTP GET or POST request.
If I send just any text, it will be displayed using default text size.
I can also use json to send settings like:

        {"t":"Some text to display", "c": "<HEX color or a predefined one>", "s": "<text size>"}

If I send a json that is missing the "t" key, the server will respond with supported text sizes and colors.

After I connect the device to network, it will display the IP address and then wait for the first message to show.
Each new message cleares the old one.

## NOTE:
There are now cheap ESP32 based LCD displays, but I wanted a linux server so I can add custom automation services. 
Also I had this hardware laying around, not usefull for anything else, so I decided to do something usefull with it. 