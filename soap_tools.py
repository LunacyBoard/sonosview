
def get_soap_from_tag(strSoap, strTag, f_unesc = True):
    """ Extract the value of a key avlue from a SOAP string
    """
    
    if f_unesc:
        lt = "<"
        ltsl = "</"
        gt = ">"
        amp = "&"
        apos = "'"
    else:
        lt = "&lt;"
        ltsl = "&lt;/"
        gt = "&gt;"
        amp = "&amp;"
        apos = "&apos;"
    
    tag_st = strSoap.find(lt + strTag + gt)
    if tag_st > 0:
        tag_st = tag_st + len(strTag) + len(lt) + len(gt)
    tag_end = strSoap.find(ltsl + strTag + gt)
    #print(tag_st,tag_end)
    strTemp = strSoap[tag_st:tag_end]
    if not f_unesc:
        strTemp = strTemp.replace(amp,"&").replace(apos,"'")
    
    return strTemp

def soap_url(base_url, service_name):
    return base_url + "MediaRenderer/" + service_name + "/Control"

def soap_body(service_name, action_name, soap_main = ""):
    """ Wrap SOAP service with suitable envelope
    """
    return """<?xml version="1.0" encoding="utf-8"?>
            <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" 
            s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>
            <u:""" + action_name + """ xmlns:u="urn:schemas-upnp-org:service:""" + service_name + """:1">
            <InstanceID>0</InstanceID>""" + soap_main + """</u:""" + action_name + """></s:Body></s:Envelope>"""

def soap_head(service_name, action_name):
    """ Prepare SOAP header for specified service
    """
    return {"soapaction" : "urn:schemas-upnp-org:service:" + service_name + ":1#" + action_name, "Content-Type" : "text/xml; charset=utf-8"}


