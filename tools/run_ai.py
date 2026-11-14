# =================================================
# This code stores AI API modules for use with auto_read.py

from google import genai
from google.genai import types
from openai import OpenAI
import base64, os
import requests
import json

from tools.api import API, GEMINI_API, OPENROUTER_API, HUNYUAN_API

or_dic = {  # OpenRouter models
    'gemini-3-pro': 'google/gemini-3-pro-preview',
    'gemini-2.5-flash': 'google/gemini-2.5-flash',
    'gpt-5': 'openai/gpt-5',
    'claude-sonnet-4.5': 'anthropic/claude-sonnet-4.5',
    'claude-opus-4.5': 'anthropic/claude-opus-4.5',
    'claude-haiku-4.5': "anthropic/claude-haiku-4.5",
    'grok-4': 'x-ai/grok-4',
    'grok-4-fast': 'x-ai/grok-4-fast',
    'grok-4.1-fast': 'x-ai/grok-4.1-fast',
    'qwen3-vl-8b-thinking': 'qwen/qwen3-vl-8b-thinking',
    'glm-4.6v': 'z-ai/glm-4.6v',  # Zhipu
    'ernie-4.5-vl-424b-a47b': 'baidu/ernie-4.5-vl-424b-a47b',  # ERNIE
}
#=====================Image recognition section======================

def run_openrouter_read(cfg, proto_img_path, grid_img_path):
    '''
    Multi-provider models (OpenRouter)
    '''

    with open(proto_img_path, 'rb') as f:
        proto_img_b64 = base64.b64encode(f.read()).decode()  # Convert to base64
    with open(grid_img_path, 'rb') as f:
        grid_img_b64 = base64.b64encode(f.read()).decode()

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API}",
        "Content-Type": "application/json",
        "Connection": 'close'
    }
    messages = [
        {
            "role": "user",
            "content": [
                    {"type": "text", "text": cfg['user_prompt']},
                    {"type": "image_url", "image_url": {'url': f"data:image/jpeg;base64,{proto_img_b64}"}},
                    {"type": "image_url", "image_url": {'url': f"data:image/jpeg;base64,{grid_img_b64}"}}
                ]
        }
    ]
    payload = {
            "model": or_dic[cfg['model']],
            "messages": messages
    }
    # requests.adapters.DEFAULT_RETRIES = 5
    response = requests.post(url, headers=headers, json=payload
                             # , verify=False
                             )
    # Check status code
    if response.status_code != 200:
        print(f"【ERROR】API request failed, status code: {response.status_code}")
        print(f'Error details: {response.text}')
        raise Exception

    if 'choices' in dict(response.json()).keys():
        ai_ans = response.json()['choices'][0]['message']['content']
        return ai_ans
    else:
        print(dict(response.json())['error'])
        raise ConnectionError(dict(response.json())['error']['message'])

def run_chatgpt_read(cfg, proto_img_path, grid_img_path):
    '''
    For ChatGPT only
    '''
    with open(proto_img_path, 'rb') as f:
        proto_img_b64 = base64.b64encode(f.read()).decode()  # Convert to base64
    with open(grid_img_path, 'rb') as f:
        grid_img_b64 = base64.b64encode(f.read()).decode()

    client = OpenAI(api_key=API)
    response = client.responses.create(
        model=cfg['model'],
        input=[
            {
                "role": "system",
                "content": cfg['prompt']
            },
            {"role": "user", "content": [
                {"type": "input_image", "image_url": f"data:image/jpeg;base64,{proto_img_b64}"},
                {"type": "input_image", "image_url": f"data:image/jpeg;base64,{grid_img_b64}"},
                {"type": "input_text", "text": cfg['user_prompt']}
            ]}
        ]
        # ,reasoning={       # Summary is unavailable; organization verification is required
        #     "effort": "medium",
        #     "summary": "auto"
        # }
    )

    ai_ans = response.output_text.strip()  # Get AI response
    # .replace(cfg['answer_strip'], '').strip()
    return ai_ans

def run_gemini_read(cfg, proto_img_path, grid_img_path):
    '''
    For Gemini only
    '''
    with open(proto_img_path, 'rb') as f:
        proto_img_bytes = f.read()
    with open(grid_img_path, 'rb') as f:
        grid_img_bytes = f.read()

    client = genai.Client(api_key=GEMINI_API)
    response = client.models.generate_content(
        model=cfg['model'],
        contents=[
            types.Part.from_bytes(
                data=proto_img_bytes,
                mime_type='image/jpeg',
            ),
            types.Part.from_bytes(
                data=grid_img_bytes,
                mime_type='image/jpeg',
            ),
            cfg['user_prompt'],
        ]
    )
    return response.text

def run_hunyuan_read(cfg, proto_img_path, grid_img_path):
    '''
    For Hunyuan only (OpenAI-compatible API)
    '''
    with open(proto_img_path, 'rb') as f:
        proto_img_b64 = base64.b64encode(f.read()).decode()  # Convert to base64
    with open(grid_img_path, 'rb') as f:
        grid_img_b64 = base64.b64encode(f.read()).decode()

    # Create client
    client = OpenAI(
        api_key=HUNYUAN_API,  # Hunyuan API key
        base_url="https://api.hunyuan.cloud.tencent.com/v1",  # Hunyuan endpoint
    )

    completion = client.chat.completions.create(
        model=cfg['model'],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": cfg['user_prompt']
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{proto_img_b64}"
                        }
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{grid_img_b64}"
                        }
                    }
                ]
            },
        ],
    )
    ai_ans = completion.choices[0].message.content

    return ai_ans

#=====================Code generation section======================

def run_gemini_code(cfg, todo_text):
    '''
    For Gemini only
    '''
    client = genai.Client(api_key=GEMINI_API)
    response = client.models.generate_content(
        model=cfg['model'],
        contents=[todo_text, cfg['contents']],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disable thinking mode to save resources
        )
    )
    return response.text

def run_chatgpt_code(cfg, todo_text):
    '''
    For ChatGPT only
    '''
    client = OpenAI(api_key=API)
    response = client.responses.create(
        model=cfg['model'],
        input=[
            {
                "role": "system",
                "content": ""
            },
            {"role": "user", "content": [
                {"type": "input_text", "text": todo_text},
                {"type": "input_text", "text": cfg['contents']}
            ]}
        ]
    )
    return response.output_text.strip()

def run_openrouter_code(cfg, todo_text):
    '''
    Multi-provider models (OpenRouter)
    '''

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API}",
        "Content-Type": "application/json",
        "Connection": 'close'
    }
    messages = [
        {
            "role": "user",
            "content": [
                    {"type": "text", "text": todo_text},
                    {"type": "text", "text": cfg['contents']},
            ]
        }
    ]
    payload = {
            "model": or_dic[cfg['model']],
            "messages": messages
    }
    # requests.adapters.DEFAULT_RETRIES = 5
    response = requests.post(url, headers=headers, json=payload
                             # , verify=False
                             )
    if 'choices' in dict(response.json()).keys():
        ai_ans = response.json()['choices'][0]['message']['content']
        return ai_ans
    else:
        print(dict(response.json())['error'])
        raise ConnectionError(dict(response.json())['error']['message'])