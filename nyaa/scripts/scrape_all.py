
import ssl 
import requests 
import os 
from requests.adapters import HTTPAdapter
from .. import util

WINDOWS = (os.name == "nt")
FILE_EXT = ("jpg","jpeg","jfif","jpe","jif","webp","png","bmp","png","ico","j2k","gif","tif","tiff")

OUTPUT_DIR = "dls\\urls\\"
URL_REGEX = (r"src=(?:\'|\")(https?://[^\'\"]*)(?:\'|\")")

class HTTPSAdapter(HTTPAdapter):

    def __init__(self, ciphers):
        context = self.ssl_context = ssl.create_default_context()
        context.options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 |
                            ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1)
        context.set_ecdh_curve("prime256v1")
        context.set_ciphers(ciphers)
        HTTPAdapter.__init__(self)

    def init_poolmanager(self, *args, **kwargs):
        kwargs["ssl_context"] = self.ssl_context
        return HTTPAdapter.init_poolmanager(self, *args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs["ssl_context"] = self.ssl_context
        return HTTPAdapter.proxy_manager_for(self, *args, **kwargs)



def _emulate_browser_firefox(session, platform):
    headers = session.headers
    headers["User-Agent"] = ("Mozilla/5.0 (" + platform + "; rv:91.0) "
                             "Gecko/20100101 Firefox/91.0")
    headers["Accept"] = ("text/html,application/xhtml+xml,"
                         "application/xml;q=0.9,image/webp,*/*;q=0.8")
    headers["Accept-Language"] = "en-US,en;q=0.5"
    headers["Accept-Encoding"] = "gzip, deflate"
    headers["Referer"] = None
    headers["Upgrade-Insecure-Requests"] = "1"
    headers["Cookie"] = None

    session.mount("https://", HTTPSAdapter(
        "TLS_AES_128_GCM_SHA256:"
        "TLS_CHACHA20_POLY1305_SHA256:"
        "TLS_AES_256_GCM_SHA384:"
        "ECDHE-ECDSA-AES128-GCM-SHA256:"
        "ECDHE-RSA-AES128-GCM-SHA256:"
        "ECDHE-ECDSA-CHACHA20-POLY1305:"
        "ECDHE-RSA-CHACHA20-POLY1305:"
        "ECDHE-ECDSA-AES256-GCM-SHA384:"
        "ECDHE-RSA-AES256-GCM-SHA384:"
        "ECDHE-ECDSA-AES256-SHA:"
        "ECDHE-ECDSA-AES128-SHA:"
        "ECDHE-RSA-AES128-SHA:"
        "ECDHE-RSA-AES256-SHA:"
        "DHE-RSA-AES128-SHA:"
        "DHE-RSA-AES256-SHA:"
        "AES128-SHA:"
        "AES256-SHA:"
        "DES-CBC3-SHA"
    ))



def main(argz = None):
    import sys 
    import re 
    
    args = argz or sys.argv[1:]

    urls = set()
    with requests.Session() as session:

        _emulate_browser_firefox(session, "Windows NT 10.0; Win64; x64")

        for url in args:
            url = url.strip()

            try:
                page = session.get(url)
            except:
                continue
            
            fatal = False
            code = page.status_code

            if code == 404:
                continue

            if 200 <= code < 400 or fatal is None and \
                    (400 <= code < 500) or not fatal and \
                    (400 <= code < 429 or 431 <= code < 500):

                for line in page.text.split("\n"):
                    for r in URL_REGEX:
                        for u in re.findall(r, line):
                            urls.add(u.strip())


    import datetime 
    from requests.utils import requote_uri
    while True:
        name = OUTPUT_DIR + str(datetime.datetime.now().timestamp()) + ".txt"

        if os.path.isfile(name):
            continue
        
        with open(name, "w") as writer:
            for line in urls:

                if util.get_url_ext(line) not in FILE_EXT:
                    continue
                
                writer.write(requote_uri(line) + "\n")

        print(name,end='')
        return





if __name__ == "__main__":
    main()



