from bs4 import BeautifulSoup
from .SearchService import SearchService
from utils import decode_unicode

import re , google.generativeai as genai

genai.configure(api_key="AIzaSyD6u75MX9eTckmbCCVAQHZQVmdmevJLhUg")

class AssignmentSolver:
    def __init__(self, client, headers_for_assignments_path, csrftokenid):
        self.client = client
        self.headers_for_assignments_path = headers_for_assignments_path
        self.csrftokenid = csrftokenid
        self.api_send_solve = ""

    async def fetch(self, url, headers):
        response = await self.client.get(url, headers=headers)
        return response

    async def fetch_post(self, url, headers, data_json=None, data_txt=None):
        response = await self.client.post(url, headers=headers, json=data_json, data=data_txt)
        return response

    async def ai(self, content):
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = await model.generate_content_async(content)
        return response.text

    async def send_solve(self, api_assignment, ask_id, answer_id, QuestionTypeCode):
        self.api_send_solve = (
            "https://schools.madrasati.sa/Student/Assignments/SolveStudentLectureAssignment"
            "?SubjectId={}&UId={}".format(
                str(api_assignment).split("&SubjectId=")[1].split("&")[0],
                str(api_assignment).split("/Student/Assignments/SolveLectureAssignment/")[1].split("?")[0]
            )
        )
        data = {
            "StudentAnswer": [{
                "Id_Enc": f"{ask_id}",
                "QuestionTypeCode": f"{QuestionTypeCode}",
                "UserAnswers": [{
                    "AnswerId_Enc": f"{answer_id}",
                    "ShortAnswer": "",
                    "ShortAnswerValid": "False"
                }],
                "MatchingQuestion": []
            }],
            "AAID": f"{api_assignment.split('/SolveLectureAssignment/')[1].split('/')[0]}",
            "SchoolId": f"{str(api_assignment).split('SchoolId=')[1].split('&')[0]}",
            "published": "false"
        }

        headers = self.headers_for_assignments_path.copy()
        headers["Requestverificationtoken"] = f"{self.csrftokenid}"
        response = await self.fetch_post(self.api_send_solve, headers=headers, data_json=data)
        if response.status_code == 200:
            print("Assignment solved successfully.")

    async def fetch_question(self, assignment_url):
        response = await self.fetch(assignment_url, headers=self.headers_for_assignments_path)
        soup = BeautifulSoup(response.text, 'html.parser')
        question_div = soup.find('div', class_='qQuestion')
        question_id = soup.find('input', class_='qid')['value']
        question_type = soup.find('input', class_='qidtype')['value']
        answers = []
        answer_elements = soup.find_all('div', class_='eldetail')
        for answer in answer_elements:
            answer_text = answer.get_text(strip=True)
            answer_id = answer.find('input', {'id': 'qaid'})['value']
            answers.append((answer_text, answer_id))
        for answer_text, answer_id in answers:
            print(f"Answer: {answer_text} - ID: {answer_id}")
            if question_type == "2":
                if "صواب" in answer_text:
                    answer_true = answer_id
                elif "خطأ" in answer_text:
                    answer_false = answer_id

        if question_div:
            question_text = question_div.get_text(strip=True)
            clean_question = question_text
            print(f"Question: {question_text}\nID: {question_id}\nType: {question_type}")
            autocomplete_result = await SearchService(self.client).autocomplete_search(question_text)
            if autocomplete_result:
                suggestions = [decode_unicode(suggestion) for suggestion in autocomplete_result]
                if suggestions:
                    clean_question = suggestions[0]
                    print(f"Suggestion: {clean_question}")

            if question_type == "2":
                ai_prompt = (
                    f"اختر الإجابة الصحيحة بناءً على النص التالي:\n{clean_question}\n"
                    f"إذا كانت الإجابة 'صواب' أرسل رقم: {answer_true}\n"
                    f"وإذا كانت 'خطأ' أرسل رقم: {answer_false}\n"
                    "تنويه ارسل فقط رقم الايدي دون اي شي اخر"
                )
            else:
                choices_text = "\n".join(
                    [f"{i + 1}. {text} (ID: {answer_id})" for i, (text, answer_id) in enumerate(answers)]
                )
                ai_prompt = (
                    f"اختر الإجابة الصحيحة للسؤال التالي:\n{clean_question}\n"
                    f"الاختيارات:\n{choices_text}\n"
                    "أرسل فقط رقم المعرف (ID) الخاص بالإجابة الصحيحة.\n"
                    "تنويه ارسل فقط رقم الايدي دون اي شي اخر"
                )
            final_answer = await self.ai(ai_prompt)
            final_answer = final_answer.strip()
            print(f"AI : {final_answer}")

            self.csrftokenid = re.search(r"var csrfToken = '(.*?)';", response.text).group(1).strip()

            await self.send_solve(assignment_url, question_id, final_answer, question_type)