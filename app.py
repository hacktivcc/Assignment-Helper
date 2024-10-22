from httpx import AsyncClient
import asyncio, sys
from auth import Login_MicrosoftApplications
from bs4 import BeautifulSoup
from quiz import AssignmentSolver
import os
from dotenv import load_dotenv, set_key


def check_credentials():
    load_dotenv()
    email = os.getenv('MADARASATI_EMAIL')
    password = os.getenv('MADARASATI_PASSWORD')
    return email, password

def save_credentials(email, password):
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    set_key(dotenv_path, 'MADARASATI_EMAIL', email)
    set_key(dotenv_path, 'MADARASATI_PASSWORD', password)

sys.stdout.reconfigure(encoding='utf-8')

class MadarasatiSa:
    def __init__(self, email=None, password=None):
        self.email = email
        self.password = password
        self.client = AsyncClient()
        self.session_state = str
        self.id_token = str
        self.state = str
        self.headers_for_schools_madrasati_sa = {}
        self.api_schools_madrasati_sa = f"https://schools.madrasati.sa/"
        self.aspnet_password = None
        self.Student_Home_Api = "https://schools.madrasati.sa"
        self.headers_for_schools_madrasati_sa_main = {}
        self.api_for_assignments_path = None
        self.headers_for_assignments_path = {}
        self.cookies = None
        self.OpenIdConnect = None
        self.csrftokenid = None
        self.assignment_solver = AssignmentSolver(self.client, self.headers_for_assignments_path, self.csrftokenid)
        
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

    async def set_headers_for_assignments_path(self):
        self.code_for_authentication, self.id_token, self.state, self.session_state, self.cookies, self.OpenIdConnect = await Login_MicrosoftApplications(self.email, self.password, self.client).return_values()

    async def get_aspnet_cookies(self):
        self.headers_for_schools_madrasati_sa = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
            "Cookie": f"{self.cookies} {self.OpenIdConnect}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = f"code={self.code_for_authentication}&id_token={self.id_token}&state={self.state}&session_state={self.session_state}"
        response = await self.fetch_post(url=self.api_schools_madrasati_sa, headers=self.headers_for_schools_madrasati_sa, data_json=None, data_txt=data)
        self.cookie_vv = response.cookies.get('.AspNet.Cookies', None)
        if response.status_code == 302:
            self.headers_for_schools_madrasati_sa.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
                "Cookie": f".AspNet.Cookies={response.cookies.get('.AspNet.Cookies', None)}"
            })

    async def get_aspnet_password(self):
        response = await self.fetch(url=self.api_schools_madrasati_sa, headers=self.headers_for_schools_madrasati_sa)
        if response.status_code == 302:
            self.aspnet_password = response.cookies.get('.AspNet.ASPNET.Password2', None)
            self.Student_Home_Api += response.text.split('Object moved to <a href="')[1].split('fromAuth=True">')[0] + "fromAuth=True"
            print(self.Student_Home_Api)
        self.headers_for_schools_madrasati_sa_main.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
            "Cookie": f".AspNet.ASPNET.Password2={self.aspnet_password}; .AspNet.Cookies={self.cookie_vv}"
        })

    async def get_paths_apis(self):
        response = await self.fetch(url=self.Student_Home_Api, headers=self.headers_for_schools_madrasati_sa_main)
        if response.status_code == 200:
            self.api_for_assignments_path = "https://schools.madrasati.sa/Student/Home/Assignments?" + response.text.split('<a href="/Student/Home/Assignments?')[1].split('">')[0].replace("&amp;", "&")
            self.headers_for_schools_madrasati_sa_main['Cookie'] += f"; IsSchoolsManager=False; IsGradeBookApproved=False; Sbadge=SB005; IsUserLoginAsFather=False; AllowFreeLessons=False; IsKindergardenUser=False; IsFather=False ; SId={response.cookies.get('SId', None)}; SchoolName={response.cookies.get('SchoolName', None)}; UId={response.cookies.get('UId', None)}"
            self.headers_for_assignments_path = self.headers_for_schools_madrasati_sa_main.copy()
            print(self.api_for_assignments_path)

    async def get_types_of_assignments(self):
        self.type1 = self.api_for_assignments_path + "&searchByStatus=Current&type=1"
        self.type2 = self.api_for_assignments_path + "&searchByStatus=Current&type=2"
        self.type3 = self.api_for_assignments_path + "&searchByStatus=Current&type=3"

    async def get_assignments_by_type(self):
        types = [self.type1, self.type2, self.type3]
        for type_url in types:
            response = await self.fetch(type_url, headers=self.headers_for_assignments_path)
            soup = BeautifulSoup(response.text, 'html.parser')
            assignment_links = soup.find_all('a', href=True)
            tasks = []
            for link in assignment_links:
                if '/Student/Assignments/SolveLectureAssignment/' in link['href']:
                    full_link = "https://schools.madrasati.sa" + link['href']
                    print(full_link)
                    tasks.append(await self.assignment_solver.fetch_question(full_link)) 
            await asyncio.gather(*tasks)

    async def run(self):
        await self.set_headers_for_assignments_path()
        await self.get_aspnet_cookies()
        await self.get_aspnet_password()
        await self.get_paths_apis()
        await self.get_types_of_assignments()
        await self.get_assignments_by_type()

    async def close(self):
        await self.client.aclose()

async def main():
    email, password = check_credentials()

    if not email or not password:
        email = input("Enter your email: ")
        password = input("Enter your password: ")
        save_credentials(email, password)

    app = MadarasatiSa(email=email, password=password)
    try:
        await app.run()
    finally:
        await app.close()

if __name__ == "__main__":
    asyncio.run(main())