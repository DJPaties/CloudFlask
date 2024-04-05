from openai import OpenAI
# import os
client = OpenAI(
    api_key="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"
)
def chat(message):
    completion = client.chat.completions.create(
        # model="gpt-4",
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": "YOu respons with the saudi law and amendement with short answers"},
        {"role": "user", "content": message}
    ]
    )
    print(type(completion.choices[0].message.content))
    return {'gpt_response':completion.choices[0].message.content, 'intent':"conversation"}

# print(chat("ما هو المصطلح الذي يعبر عن فلسفة البوذية؟"))