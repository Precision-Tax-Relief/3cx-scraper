from time import sleep

import pandas
import requests

SEGMENT_WEBHOOK_URL = 'https://fn.segmentapis.com/?b=YkNxeTVzMlRSVWFzTEtiMjF1aVJnWTo6RkFjZ1hXNE12cGxhUE5uRUVFS2Z1clBYTkRWSGJQZjg='

if __name__ == '__main__':
    csv_file = 'downloads/typeform_fb.csv'
    df = pandas.read_csv(csv_file)
    # fill all NaN with empty string
    df = df.fillna('')

    treatment_headers = [
        'Skin Tightening',
        'Wrinkle Reduction',
        'Skin Clarity/Texture Improvements',
        'Volumizing',
        'Sculpting',
        'Lifting',
        'Vaginal Rejuvination',
        'Hair Reduction',
        'Tattoo Removal',
    ]

    answers_list = []
    for row in df.iterrows():
        requested_treatments = [row[1][header] for header in treatment_headers if row[1][header] != '']
        answers_list.append({
            'formTitle': 'Sarah Hamilton Face | Book Your Consultation (FB Ads)',
            'formId': 'xFM5uHHb',
            'responseId': row[1]['#'],
            'location': row[1]['WELCOME!\n\nWhich location is closest to you?'],
            'treatments': requested_treatments,
            'other_treatments': row[1]['Other'],
            'first': row[1]['First name'],
            'last': row[1]['Last name'],
            'phone': row[1]['Phone number'].replace("'", ""),
            'email': row[1]['Email'],
            'best_time': row[1]["Alright, what's the best time for our team to reach out to you?"],
            'submitted_at': row[1]['Submit Date (UTC)'],
            'land_time': row[1]['Start Date (UTC)'],
        })

    for answers in answers_list[28:]:
        typeform_payload = {
            "event_type": "form_response",
            "form_response": {
                "form_id": "D01tRWkE",
                "token": answers['responseId'],
                "landed_at": answers['land_time'],
                "submitted_at": answers['submitted_at'],
                "definition": {
                    "id": "D01tRWkE",
                    "title": "Sarah Hamilton Face | Book Your Consultation (Google Ads)",
                    "fields": [
                        {
                            "id": "mMGwZGAyTvf1",
                            "ref": "01GG6MX757CA4R148AZCT47RR3",
                            "type": "multiple_choice",
                            "title": "WELCOME!\n\nFirst off we'd love to know which Sarah Hamilton Face location you're closest to?",
                            "properties": {},
                            "choices": [
                                {
                                    "id": "hIvRGTzyIj18",
                                    "ref": "01GG6MX757AYBNV0BZP8YM14GR",
                                    "label": "Liberty Lake, Washington"
                                },
                                {
                                    "id": "meeCV4IquYE1",
                                    "ref": "01GG6MX757NVZY93ZAAA213X8A",
                                    "label": "Coeur d'Alene, Idaho"
                                }
                            ]
                        },
                        {
                            "id": "oSvHRtQ0Qnks",
                            "ref": "ac7da37b-8543-4621-bcf8-eb00fb886144",
                            "type": "multiple_choice",
                            "title": "Great! Now what types of treatment's are you most interested in?",
                            "properties": {},
                            "allow_multiple_selections": True,
                            "allow_other_choice": True,
                            "choices": [
                                {
                                    "id": "EnDjOGccFxYo",
                                    "ref": "8d8595e9-5f59-412c-a79e-741dc8379ef2",
                                    "label": "Skin Tightening"
                                },
                                {
                                    "id": "RCIrZtWTHrhM",
                                    "ref": "051be3eb-d929-4783-87bf-ad77c8547a13",
                                    "label": "Wrinkle Reduction"
                                },
                                {
                                    "id": "jqPADcj7CSqg",
                                    "ref": "00bd814b-a098-466a-ae7f-15c1a427589f",
                                    "label": "Skin Clarity/Texture Improvements"
                                },
                                {
                                    "id": "sds9GkYaz9s3",
                                    "ref": "cfe3dddf-463f-4833-badc-78b3320e2cb8",
                                    "label": "Volumizing"
                                },
                                {
                                    "id": "LTeKBr5oymFP",
                                    "ref": "bff4f1ee-b211-46dc-9277-6a6dbd51f830",
                                    "label": "Sculpting"
                                },
                                {
                                    "id": "KryxfSifpObH",
                                    "ref": "737e8475-f6a4-454e-84a5-83cf84f4b6b9",
                                    "label": "Lifting"
                                },
                                {
                                    "id": "DC846WQYiniv",
                                    "ref": "44b6591f-fed5-40f7-acab-854ea09c0328",
                                    "label": "Vaginal Rejuvination"
                                },
                                {
                                    "id": "V5wZ3auDH97e",
                                    "ref": "fe856261-945a-48ec-899e-58ebe99d7e40",
                                    "label": "Hair Reduction"
                                },
                                {
                                    "id": "1jBGORQXkxcc",
                                    "ref": "a938a617-0c2b-44ee-ae8f-e0574bd73b1d",
                                    "label": "Tattoo Removal"
                                }
                            ]
                        },
                        {
                            "id": "R2bM7XGoLtX2",
                            "ref": "cbd0500c-2442-4999-b6ed-5243a45859c3",
                            "type": "short_text",
                            "title": "First name",
                            "properties": {}
                        },
                        {
                            "id": "1iKu1kUgwlYk",
                            "ref": "c5771ef1-94e8-46af-a62e-5940ca4b9841",
                            "type": "short_text",
                            "title": "Last name",
                            "properties": {}
                        },
                        {
                            "id": "bT72Egeguy1p",
                            "ref": "4eac6de2-62ad-4a6e-9f6b-985b61c0b55b",
                            "type": "phone_number",
                            "title": "Phone number",
                            "properties": {}
                        },
                        {
                            "id": "rFy1NxB44HJW",
                            "ref": "0d7238dd-d5a5-42da-a5fb-56316df13357",
                            "type": "email",
                            "title": "Email",
                            "properties": {}
                        },
                        {
                            "id": "YXu25K6S1u8r",
                            "ref": "eea7e9b1-fc86-4c0c-bd37-ce573df9feee",
                            "type": "multiple_choice",
                            "title": "Alright, what's the best time for our team to reach out to you?",
                            "properties": {},
                            "choices": [
                                {
                                    "id": "dsb6lHuPWmLQ",
                                    "ref": "a931ba04-404b-42a2-850b-9f0e1434a7c8",
                                    "label": "Morning"
                                },
                                {
                                    "id": "vpuwUG1Hvn6i",
                                    "ref": "adcd0628-eaf5-480f-9864-b1de7f5381e8",
                                    "label": "Mid-Day"
                                },
                                {
                                    "id": "FPHK7Y9bF6TW",
                                    "ref": "f66691a2-b13b-4db1-9944-422759a712ef",
                                    "label": "Afternoon"
                                }
                            ]
                        }
                    ]
                },
                "answers": [
                    {
                        "type": "choice",
                        "choice": {
                            "id": "meeCV4IquYE1",
                            "label": answers['location'],
                            "ref": "01GG6MX757NVZY93ZAAA213X8A"
                        },
                        "field": {
                            "id": "mMGwZGAyTvf1",
                            "type": "multiple_choice",
                            "ref": "01GG6MX757CA4R148AZCT47RR3"
                        }
                    },
                    {
                        "type": "choices",
                        "choices": {
                            "labels": answers['treatments'],
                        },
                        "field": {
                            "id": "oSvHRtQ0Qnks",
                            "type": "multiple_choice",
                            "ref": "ac7da37b-8543-4621-bcf8-eb00fb886144"
                        }
                    },
                    {
                        "type": "text",
                        "text": answers['first'],
                        "field": {
                            "id": "R2bM7XGoLtX2",
                            "type": "short_text",
                            "ref": "cbd0500c-2442-4999-b6ed-5243a45859c3"
                        }
                    },
                    {
                        "type": "text",
                        "text": answers['last'],
                        "field": {
                            "id": "1iKu1kUgwlYk",
                            "type": "short_text",
                            "ref": "c5771ef1-94e8-46af-a62e-5940ca4b9841"
                        }
                    },
                    {
                        "type": "phone_number",
                        "phone_number": answers['phone'],
                        "field": {
                            "id": "bT72Egeguy1p",
                            "type": "phone_number",
                            "ref": "4eac6de2-62ad-4a6e-9f6b-985b61c0b55b"
                        }
                    },
                    {
                        "type": "email",
                        "email": answers['email'],
                        "field": {
                            "id": "rFy1NxB44HJW",
                            "type": "email",
                            "ref": "0d7238dd-d5a5-42da-a5fb-56316df13357"
                        }
                    },
                    {
                        "type": "choice",
                        "choice": {
                            "label": answers['best_time'],
                        },
                        "field": {
                            "id": "YXu25K6S1u8r",
                            "type": "multiple_choice",
                            "ref": "eea7e9b1-fc86-4c0c-bd37-ce573df9feee"
                        }
                    }
                ]
            }
        }
        if answers['other_treatments'] != '':
            typeform_payload['form_response']['answers'][1]['choices']['other'] = answers['other_treatments']

        # send http data to segment webhook url
        response = requests.post(SEGMENT_WEBHOOK_URL, json=typeform_payload)
        from pprint import pprint
        pprint(answers)
        print(response.status_code)
        print(response.text)
        sleep(15)

        # for question in questions:
        #     answer_key = f'{question["id"]}-{answers["responseId"]}'
        #     data = {
        #         'formId': answers['formId'],
        #         'responseId': answers['responseId'],
        #         'questionId': question['id'],
        #         'type': question['type'],
        #         'answer': answers[question['id']]
        #     }
        #     if data['answer'] != '':
        #         analytics.object(object_id=answer_key, collection='form_answers', properties=data)
        #
        # form_response = {
        #     'formId': answers['formId'],
        #     'submitTime': answers['submitted_at'],
        #     'landTime': answers['land_time'],
        #     'formTitle': answers['formTitle'],
        # }
        # analytics.object(object_id=answers['responseId'], collection='form_responses', properties=form_response)