import os
import openai
from dotenv import load_dotenv
from duckduckgo_search import ddg_images

# key oepnai
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_artikel(keyword):
    completion = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"create article {keyword} intoduction and step by step",
        max_tokens=2097,
        temperature=0.5
    )
    text = completion.choices[0].text
    text = text.replace('Introduction','')
    return text

def get_image(keyword, count_paragraph=10):
    inline_images = ddg_images(
        keyword, 
        region='wt-wt', 
        safesearch='Off', 
        size='Large',
        color='color', 
        type_image='photo', 
        layout=None, 
        license_image=None, 
        max_results=count_paragraph+3
    )
    list_url_images = [inline_image['image'] for inline_image in inline_images]
    return list_url_images

