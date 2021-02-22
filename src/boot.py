import etc
import network
import ntptime
import time


# CONNECT TO NETWORK
wifi_settings = etc.get_config('wifi.json')
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

while not wlan.isconnected():
    available_networks = [x[0].decode('utf-8') for x in wlan.scan()]
    for wifi in wifi_settings:
        if wifi['SSID'] in available_networks:
            print("Connecting to {}".format(wifi['SSID']))
            wlan.connect(wifi['SSID'], wifi['password'])
            time.sleep(5)
            if not wlan.isconnected():
                wlan.disconnect()

    if not wlan.isconnected():
        print("Could not connect to a known network")
        print(available_networks)
        time.sleep(5)

# SET TIME
try:
    ntptime.settime()
except OSError:
    time.sleep(1)
    try:
        ntptime.settime()
    except OSError:
        pass
