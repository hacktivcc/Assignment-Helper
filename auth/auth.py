import uuid
from cookies import CookieGenerator
from telemetry import Genereter_Telemetry_Data
import time
import re
from urllib.parse import urlencode

class MicrosoftApplicationsTelemetryDeviceId:
    def __init__(self):
        self.MicrosoftApplicationsTelemetryDeviceId_P = uuid.uuid4()
    def return_value(self):
        return self.MicrosoftApplicationsTelemetryDeviceId_P


class Login_MicrosoftApplications:
    def __init__(self, email=None, password=None, Client=None):
        self.email = email
        self.password = password
        self.auth_login_api = 'https://schools.madrasati.sa/Auth/SignIn'
        self.getcredentialtype_api = 'https://login.microsoftonline.com/common/GetCredentialType?mkt=ar'
        self.headers_credent = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"
        }
        self.oauth2_api = ''
        self.data_credentials = {
            "username": self.email,
            "isOtherIdpSupported": False,
            "checkPhones": True,
            "isRemoteNGCSupported": True,
            "isCookieBannerShown": False,
            "isFidoSupported": True,
            "country": "SA",
            "forceotclogin": False,
            "isExternalFederationDisallowed": False,
            "isRemoteConnectSupported": False,
            "federationFlags": 0,
            "isSignup": False,
            "isAccessPassSupported": True,
            "isQrCodePinSupported": True
        }
        self.data_login = {}
        self.headers_login = {}
        self.secret = None
        self.OpenIdConnect = None
        self.client = Client
        self.MicrosoftApplicationsTelemetryDeviceId = MicrosoftApplicationsTelemetryDeviceId().return_value()
        self.cookies = CookieGenerator(self.MicrosoftApplicationsTelemetryDeviceId).generate_initial_cookies()
        self.start_time = time.time()

    def extract_dynamic_cookie(self, cookies, pattern):
        for cookie in cookies:
            cookie_parts = cookie.split("=")
            if len(cookie_parts) == 2:
                if re.match(pattern, cookie_parts[0]):
                    return cookie_parts[0], cookie_parts[1]
        return None, None

    def update_cookies(self, response):
        cookies = response.cookies
        if cookies:
            cookie_header = "; ".join([f"{cookie.name}={cookie.value}" for cookie in cookies.jar])
            if 'Cookie' in self.headers_credent:
                self.headers_credent['Cookie'] += "; " + cookie_header
            else:
                self.headers_credent['Cookie'] = cookie_header

    async def _prepare_headers(self, headers):
        if 'Cookie' in headers:
            if self.cookies not in headers['Cookie']:
                headers['Cookie'] += "; " + self.cookies
        else:
            headers['Cookie'] = self.cookies
        return headers

    async def fetch(self, url, headers):
        headers = await self._prepare_headers(headers)
        response = await self.client.get(url, headers=headers)

        return response

    async def fetch_post(self, url, headers, data_json=None, data_txt=None):
        headers = await self._prepare_headers(headers)
        response = await self.client.post(url, headers=headers, json=data_json, data=data_txt)
        return response

    async def set_param(self):
        response = await self.fetch(self.auth_login_api, {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0'
        })
        self.oauth2_api += response.headers['Location']
        self.OpenIdConnect = response.headers['Set-Cookie']

    async def login_to_oauth2(self):
        response = await self.fetch(self.oauth2_api, {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
            'Sec-Gpc': '1',
            'Dnt': '1'
        })
        if response.status_code == 200:
            cookies = response.cookies
            cookie_header = "; ".join([f"{cookie.name}={cookie.value}" for cookie in cookies.jar])
            self.headers_credent['Cookie'] = cookie_header + "; x-ms-gateway-slice=estsfd; stsservicecookie=estsfd; brcap=0"
            self.data_credentials['originalRequest'] = response.text.split('"code","sCtx":')[1].split(',"iProductIcon"')[0].replace('"', '').replace(" ", '')
            self.data_credentials['flowToken'] = response.text.split('"sPOST_Username":"","sFT":')[1].split(',"sFTName"')[0].replace('"', '').replace(" ", '')
            time_on_page = int(time.time() - self.start_time)
            i19_value = min(time_on_page, 15392)
            self.data_login.update({
                'i13': '0',
                'login': self.email.replace("@", "%40"),
                'type': '11',
                'LoginOptions': '3',
                'lrt': '',
                'lrtPartition': '',
                'hisRegion': '',
                'hisScaleUnit': '',
                'passwd': self.password,
                'ps': '2',
                'psRNGCDefaultType': '',
                'psRNGCEntropy': '',
                'psRNGCSLK': '',
                'canary': response.text.split('"ConvergedSignIn","apiCanary":')[1].split('"canary":"')[1].split('","sCanaryTokenName"')[0].replace('"', ''),
                'ctx': self.data_credentials['originalRequest'],
                'hpgrequestid': response.headers['x-ms-request-id'],
                'flowToken': self.data_credentials['flowToken'],
                'PPSX': '',
                'NewUser': '1',
                'FoundMSAs': '',
                'fspost': '0',
                'i21': '0',
                'CookieDisclosure': '0',
                'IsFidoSupported': '1',
                'isSignupPost': '0',
                'DfpArtifact': '',
                'i19': i19_value,
                'loginfmt': self.email.replace("@", "%40")
            })
            self.headers_login = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
                "Content-Type": "application/x-www-form-urlencoded",
                "Cookie": cookie_header + "; x-ms-gateway-slice=estsfd; stsservicecookie=estsfd; brcap=0; wlidperf=FR=L&ST=1727785305534;",
            }

    async def get_credential_type(self):
        response = await self.fetch_post(self.getcredentialtype_api, self.headers_credent, data_json=self.data_credentials)
        if response.status_code == 200:
            self.secret = response.headers['Set-Cookie'].replace("fpc=", "")
            del self.data_credentials['flowToken']
            self.data_credentials['flowToken'] = response.text.split('"FlowToken":"')[1].split('","IsSignupDisallowed"')[0]

    async def send_telemetry_data(self):
        url = "https://eu-mobile.events.data.microsoft.com/OneCollector/1.0/?cors=true&content-type=application/x-json-stream&w=0"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
            "Client-Id": "NO_AUTH",
            "Client-Version": "1DS-Web-JS-3.2.6",
            "Apikey": "b0c252808e614e949086e019ae1cb300-e0c02060-e3b3-4965-bd7c-415e1a7a9fde-6951",
            "Upload-Time": str(int(time.time() * 1000)),
            "Time-Delta-To-Apply-Millis": "use-collector-delta",
            "Content-Type": "application/x-json-stream"
        }
        data = Genereter_Telemetry_Data(self.MicrosoftApplicationsTelemetryDeviceId).return_value()
        response = await self.client.post(url, headers=headers, data=data)
        if response.status_code == 200:
            response_json = response.json()
            msfpc_value = response_json.get('webResult', {}).get('msfpc')
            return msfpc_value if msfpc_value else None
        else:
            return None

    async def get_headers_login(self, msfpc):
        url = "https://login.microsoftonline.com/common/login"
        post_data = urlencode(self.data_login).replace("%2540", "%40")
        if msfpc:
            self.headers_login['Cookie'] += f" msfpc={msfpc}"
        response = await self.fetch_post(url, self.headers_login, data_json=None, data_txt=post_data)
        if response.status_code == 200:
            cookies = response.cookies.jar
            cookie_dict = {cookie.name: cookie.value for cookie in cookies}
            buid = cookie_dict.get("buid")
            esctx = cookie_dict.get("esctx")
            fpc = cookie_dict.get("fpc")
            ests_auth_persistent = cookie_dict.get("ESTSAUTHPERSISTENT")
            ests_auth = cookie_dict.get("ESTSAUTH")
            ests_auth_light = cookie_dict.get("ESTSAUTHLIGHT")
            canary = re.search(r'"canary":"(.*?)"', response.text).group(1)
            dynamic_cookies = {name: value for name, value in cookie_dict.items() if re.match(r'esctx-.*', name)}
            hpgrequestid = response.headers.get("x-ms-request-id")
            ctx = re.search(r'"sCtx":"(.*?)"', response.text).group(1)
            flow_token = re.search(r'"sFT":"(.*?)"', response.text).group(1)
            return buid, esctx, dynamic_cookies, fpc, ests_auth_persistent, ests_auth, ests_auth_light,hpgrequestid,ctx,flow_token,canary
        else:
            print(f"Failed to fetch headers login: {response.status_code}")
            return None

    async def send_kmsi_request(self, buid, esctx, dynamic_cookies, fpc, flow_token, canary, i19_value, ests_auth_persistent, ests_auth, ests_auth_light,hpgrequestid,ctx):
        url = "https://login.microsoftonline.com/kmsi"

        cookie_header = (
            f"buid={buid}; "
            f"esctx={esctx}; "
            f"fpc={fpc}; "
            f"ESTSAUTHPERSISTENT={ests_auth_persistent}; "
            f"ESTSAUTH={ests_auth}; "
            f"ESTSAUTHLIGHT={ests_auth_light}; "
        )

        for name, value in dynamic_cookies.items():
            cookie_header += f"{name}={value}; "

        cookie_header = cookie_header.strip()

        headers = {
            "Host": "login.microsoftonline.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": cookie_header
        }

        data = f"LoginOptions=1&type=28&ctx={ctx}&hpgrequestid={hpgrequestid}&flowToken={flow_token}&canary={canary}&i19={i19_value}"

        response = await self.client.post(url, headers=headers, data=data)
        
        if response.status_code == 200:
            code_for_authentication = response.text.split('<input type="hidden" name="code" value="')[1].split('" />')[0]
            id_token = response.text.split('<input type="hidden" name="id_token" value="')[1].split('" />')[0]
            state = response.text.split('<input type="hidden" name="state" value="')[1].split('" />')[0]
            session_state = response.text.split('<input type="hidden" name="session_state" value="')[1].split('" />')[0]
            return  code_for_authentication, id_token, state, session_state, self.cookies , self.OpenIdConnect
        return None
    async def return_values(self):
        await self.set_param()
        await self.login_to_oauth2()
        await self.get_credential_type()
        msfpc = await self.send_telemetry_data()
        buid, esctx, dynamic_cookies, fpc, ests_auth_persistent, ests_auth, ests_auth_light,hpgrequestid,ctx,flow_token,canary = await self.get_headers_login(msfpc)
        return await self.send_kmsi_request(buid, esctx, dynamic_cookies, fpc, flow_token, canary, self.data_login['i19'], ests_auth_persistent, ests_auth, ests_auth_light,hpgrequestid,ctx)