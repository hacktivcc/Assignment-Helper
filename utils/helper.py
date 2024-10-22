def encode_unicode(data: str):
    try:
        return data.encode('utf-8').decode('latin1')
    except:
        return data

def decode_unicode(data: str):
    try:
        return data.encode('latin1').decode('utf-8')
    except:
        return data
