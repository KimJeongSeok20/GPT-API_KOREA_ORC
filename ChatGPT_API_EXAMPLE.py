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
    
    # 숫자와 공백을 제거하는 정규 표현식
    cleaned_matches = [re.sub(r'[0-9\s,]', '', match) for match in matches]
    
    return set(cleaned_matches)

def matching_chars(description, given_word):
    # 숫자와 공백을 제거한 후 비교
    cleaned_description = re.sub(r'[0-9\s]', '', description)
    cleaned_given_word = re.sub(r'[0-9\s]', '', given_word)
    match_count = sum(1 for char in cleaned_given_word if char in cleaned_description)
    thres = int(len(max(cleaned_given_word, cleaned_description)) * (2 / 3)) # 두 단어중 긴 단어를 기준으로 2 / 3으로 잡음
    return match_count >= thres
    
# OpenAI 클라이언트 설정
client = OpenAI(
    api_key=""
)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# 이미지 파일 경로
image_file_path = "./ki/4.jpg"
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
text = ""
prompt = "이거 어떻게 사용해"
output = get_response(image_url=image_path, prompt=prompt)
print(output)

ocr.run_ocr(image_file_path, debug=False)
# 추가 질문 루프
while True:
    text = input("추가 질문 : ")
    if text == "X":
        break
    prompt = f"이미지에 대한 질문사항을 받을텐데 그 질문을 해결하기 위한 순차적 행동을 다음과 같은 형식으로 알려줘: \n1-step.....\n2-step... ... N-step... \
              만약 해당 이미지로 n-step의 내용을 다 설명하기 힘들다고 판단하면 이미지 정보를 볼때 행동 가능한 n-step을 도출한뒤 다음과 같이 대답해줘: '''더 자세한 설명을 위해 추가적인 정보를 입력해주세요!''' \
              행동을 알려줄때는 반드시 이미지에서 보이는 텍스트 정보를 포함해서 설명해줘. 현재 이미지에서 할 수 없는 행동을 알려주면 안돼.\
              이미지를 통해 알 수 없는 정보들은 대답으로 내놓으면 안돼.\
              답변에 있는 텍스트가 이미지에도 있으면 #<text>#와 같은 형식으로 대답해줘.\
              해당 이미지를 통해 대답을 하기 어렵다면 다음과 같은 형식으로 답변해: '''해당 이미지 정보로는 답변을 드리기 어렵습니다. 다양한 이미지 정보를 입력해주세요!'''\
              만약 해당 질문이 n-step의 형식으로 대답하기 힘든 질문일 경우는 최대한 간단하고 간결하게 답해줘. 예를 들어: '''카드 투입기가 어딨어?'''라는 질문이 들어오면\
              '''카드 투입기의 위치를 표시했습니다. 확인해보세요'''이런 식으로\
              질문이 없거나 이해하기 어려운 방식의 질문, 예를 들어 질문이 '''....,?나어ㅣ낭러ㅏ'''와 같이 들어오면 다음과 같이 대답해줘: '''죄송합니다. 다시 질문해주세요'''\
                \n\n\n{text}\n\n\n"
    output = get_response(image_url=image_path, prompt=prompt)
    extracted_texts = extract_text_in_hashes(output)
    print(extracted_texts)
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
