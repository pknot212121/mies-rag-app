
import base64
from openai import OpenAI
import os
import scipdf
from google import genai
from google.genai import types
import re
import shutil

gemini_api_key=os.getenv("GEMINI_API_KEY")

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def get_figures_and_tables_from_papers(output,full_path):
    shutil.rmtree(output, ignore_errors=True)
    os.makedirs(output, exist_ok=True)

    if os.path.isfile(full_path):
        scipdf.parse_figures(full_path, output_folder=output)
        print(full_path + " finished")

def analyze_figures_and_tables_with_gemma(folder):
    client = genai.Client(api_key=gemini_api_key)
    responses = []
    for filename in os.listdir(folder):
        full_path = os.path.join(folder, filename)
        if os.path.isfile(full_path):
            with open(full_path, 'rb') as f:
                image_bytes = f.read()

            response = client.models.generate_content(
                model='gemma-3-27b-it',
                contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type='image/png',
                ),
                'Describe the contents of this image and extract all important information.'
                ]
            )
            if("Figure" in filename):
                res = "<this is a description of an image> " + response.text + "</this is a description of an image>"
            elif("Table" in filename):
                res = "<this is a description of a table>" + response.text + "</this is a description of a table>"
            print(res)
            responses.append(res)
            # name = re.sub('.png','',filename)
            # with open(os.path.join(output_folder,name)+".txt",'w') as f:
            #     f.write(response.text)
    return responses
# get_figures_and_tables_from_papers("outputs","input/12550.pdf")
# l = analyze_figures_and_tables_with_gemma("outputs/figures")
# print("aaa")