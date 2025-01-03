import requests
from docx import Document

# مسار ملف الـ docx
docx_file = "script.docx"

# قراءة النص من ملف docx
def read_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

# إعداد المتغيرات الخاصة بواجهة API
CHUNK_SIZE = 1024
url = "https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB"
headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": "ضع مفتاحك هنا"
}

# قراءة النص من ملف docx
text_from_docx = read_docx(docx_file)

# البيانات المرسلة إلى API
data = {
    "text": text_from_docx,  # النص المأخوذ من ملف docx
    "model_id": "eleven_multilingual_v2",  # Use the multilingual model to support Arabic
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.5
    }
}

# إرسال الطلب إلى API
response = requests.post(url, json=data, headers=headers)

# حفظ الملف الصوتي الناتج
with open('output.mp3', 'wb') as f:
    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
        if chunk:
            f.write(chunk)

print("Voice generated and saved as output.mp3")
