from OLED_2inch23 import OLED_2inch23
import network
import urequests
from xml.etree import ElementTree

import soap_tools as ST
import secrets
import time

OLED = OLED_2inch23()

OLED.fill_screen(row1="SONOS Viewer",row3="...connecting...")

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

wlan.connect(secrets.SSID1, secrets.PASSWORD)
sonos_net = ""
base_url = "http://" + secrets.SONOS_IP + ":1400/"

# Wait for connect or fail
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

# Handle connection error
if wlan.status() != 3:
    # Try the other network
    wlan.connect(secrets.SSID2, secrets.PASSWORD)
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)
    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected to ' + secrets.SSID2 )
        sonos_net = secrets.SSID2
        OLED.text(secrets.SSID2,1,12,OLED.white)
        OLED.show()
        status = wlan.ifconfig()
        print( 'ip = ' + status[0] )
    
else:
    print('connected to ' + secrets.SSID1 )
    sonos_net = secrets.SSID1
    OLED.text(secrets.SSID1,1,12,OLED.white)
    OLED.show()
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )
    


# Get SONOS Status
r = urequests.request( method = "POST", url = ST.soap_url(base_url,"AVTransport"),
                       headers = ST.soap_head("AVTransport","GetTransportInfo"),
                       data = ST.soap_body("AVTransport","GetTransportInfo"))
print(r.status_code)
sonos_status = ST.get_soap_from_tag(r.text, "CurrentTransportState")
print(sonos_status)
r.close()
OLED.fill_screen(row2=sonos_net,row3=sonos_status)

while sonos_status == "PLAYING":
    r = urequests.request( method = "POST", url = ST.soap_url(base_url,"AVTransport"),
                       headers = ST.soap_head("AVTransport","GetPositionInfo"),
                       data = ST.soap_body("AVTransport","GetPositionInfo"))
    #print(r.text)
    sonos_trackno = ST.get_soap_from_tag(r.text, "Track")
    sonos_durtime = ST.get_soap_from_tag(r.text, "TrackDuration")
    sonos_reltime = ST.get_soap_from_tag(r.text, "RelTime")
    print(sonos_durtime,sonos_reltime)
    dursecs = (int(sonos_durtime[2:4])*60) + int(sonos_durtime[5:7])
    relsecs = (int(sonos_reltime[2:4])*60) + int(sonos_reltime[5:7])
    print(dursecs, relsecs, relsecs/dursecs)
    sonos_meta = ST.get_soap_from_tag(r.text, "TrackMetaData")
    sonos_artist = ST.get_soap_from_tag(sonos_meta, "r:albumArtist", False)
    if len(sonos_artist) == 0:
        sonos_artist = ST.get_soap_from_tag(sonos_meta, "dc:creator", False)
    sonos_artist = sonos_artist + ("... " if len(sonos_artist) > 16 else "")
    sonos_album = ST.get_soap_from_tag(sonos_meta, "upnp:album", False)
    sonos_album = sonos_album + ("... " if len(sonos_album) > 16 else "")
    sonos_track = ST.get_soap_from_tag(sonos_meta, "dc:title", False)
    track_info = sonos_track + ("... "  if len(sonos_track) > 16 else "")
    last_track = sonos_track
    cnt = 0
    OLED.fill_screen(row1 = sonos_artist, row2 = sonos_album, row3 = track_info, progress = relsecs/dursecs)
    
    while last_track == sonos_track:
        time.sleep(1)
        cnt = cnt + 1
        relsecs = relsecs + 1
            
        sonos_artist = OLED.scroller(sonos_artist)
        sonos_album = OLED.scroller(sonos_album)
        track_info = OLED.scroller(track_info)
        OLED.fill_screen(row1 = sonos_artist, row2 = sonos_album, row3 = track_info, progress = relsecs/dursecs)
        
        if cnt % 10 == 0:
            r = urequests.request( method = "POST", url = ST.soap_url(base_url,"AVTransport"),
                       headers = ST.soap_head("AVTransport","GetPositionInfo"),
                       data = ST.soap_body("AVTransport","GetPositionInfo"))
            sonos_meta = ST.get_soap_from_tag(r.text, "TrackMetaData")
            sonos_track = ST.get_soap_from_tag(sonos_meta, "dc:title", False)
            sonos_reltime = ST.get_soap_from_tag(r.text, "RelTime")
            relsecs = (int(sonos_reltime[2:4])*60) + int(sonos_reltime[5:7])
                
    # Check if still playing
    r = urequests.request( method = "POST", url = ST.soap_url(base_url,"AVTransport"),
                       headers = ST.soap_head("AVTransport","GetTransportInfo"),
                       data = ST.soap_body("AVTransport","GetTransportInfo"))
    sonos_status = ST.get_soap_from_tag(r.text, "CurrentTransportState")
    
    
    
OLED.fill_screen(row3="DONE")
