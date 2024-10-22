import json,urllib.parse
from utils import decode_unicode

def encode_url(text):
    return urllib.parse.quote(text)

class SearchService:
    def __init__(self, Client):
        self.url = "https://fast-answer.mixksa.com/search"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
        }
        self.client = Client

    async def autocomplete_search(self,question_text):
        question_text_enc = encode_url(question_text)
        url = f"https://fast-answer.mixksa.com/autocomplete?query={question_text_enc}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
        }

        response = await self.client.get(url, headers=headers)
        if response.status_code == 200:
            try:
                response_json = json.loads(response.text)
                decoded_suggestions = [decode_unicode(suggestion) for suggestion in response_json]
                return decoded_suggestions
            except json.JSONDecodeError:
                return None
        else:
            return None



    async def search_question(self, query):
        data = {
            "query": query
        }
        response = await self.client.post(self.url, headers=self.headers, data=data)
        decoded_response = decode_unicode(response.text.strip())
        decoded_response = json.loads(decoded_response)

        if 'answer' in decoded_response:
            return decoded_response['answer'].strip()
        else:
            return "No answer found"
        