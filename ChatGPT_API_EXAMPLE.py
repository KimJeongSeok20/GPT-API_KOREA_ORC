import io
import base64
from openai import OpenAI
import PIL
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import re
from main import PororoOcr


PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
ocr = PororoOcr()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def extract_text_in_hashes(text):
    # 정규 표현식을 사용하여 #{text}# 패턴에 해당하는 텍스트를 추출
    pattern = r'#(.*?)#'
    matches = re.findall(pattern, text)
    return set(matches)

def matching_chars(description, given_word):
    match_count = sum(1 for char in given_word if char in description)
    return match_count >= 2
    
# OpenAI 클라이언트 설정
client = OpenAI(
    api_key="sk-tJjZZ2RdHzgtg087_Te63TtV2rNxYoHxwCT73tBTHeT3BlbkFJ1fTGPO6icWjCNgZo5MclVxP7GAm_AxNIJC-2sDY5QA"
)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# 이미지 파일 경로
image_file_path = "./remotecontroller.jpg"
base64_image = encode_image(image_file_path)
image_path = f"data:image/png;base64,{base64_image}"

def get_response(image_url, prompt, model="gpt-4o", temperature=0):
    message = [
        {"role": "system", "content": "너는 노인분들의 전자기기 사용을 도와줄 도우미야. 이미지에 대한 직관적이고 이해하기 쉬운 설명을 하도록! "},
        {"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {
                "url": image_url
            }}
        ]}
    ]
    response = client.chat.completions.create(
        model=model,
        messages=message,
        temperature=temperature,
    )

    return response.choices[0].message.content

img = Image.open(image_file_path)        
plt.imshow(img)
plt.axis('off') 
plt.show()

# 이미지 캡쳐시
text = "이거 어떻게 사용해"
prompt = ""
output = get_response(image_url=image_path, prompt=prompt)
print(output)

ocr.run_ocr(image_file_path, debug=False)
# 추가 질문 루프
while True:
    text = input("추가 질문 : ")
    if text == "X":
        break
    prompt = f"너가 이미지를 받고 질문을 받으면 이러한 형식으로 작성해:\n1-step.....\n2-step... ... N-step...\n그리고 만약 대답에서 나온 text가 이미지에 있으면 그 텍스트는 #{text}# 이러한 방식으로 샵사이에 작성해줘"
    output = get_response(image_url=image_path, prompt=prompt)
    extracted_texts = extract_text_in_hashes(output)

    for num,descript in enumerate(ocr.get_ocr_result()["description"]):
        for extract in extracted_texts:
            if matching_chars(descript,extract):
                img = Image.open(image_file_path).convert('RGB')
                draw = ImageDraw.Draw(img)
                left_upper=ocr.get_ocr_result()["bounding_poly"][num]["vertices"][0]
                right_lower=ocr.get_ocr_result()["bounding_poly"][num]["vertices"][2]
                draw.rectangle((left_upper['x'],left_upper['y'],right_lower['x'],right_lower['y']), outline=(255,0,0), width = 5)
    img.show()

    print(output)