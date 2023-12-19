#!/bin/bash
rm -rf segment
cp -r /Users/logan/rufsoft/analytics-python/segment segment

docker-compose down
docker-compose build
docker-compose up -d

sleep 1

echo "Starting task..."
# Invoke the function
curl "http://localhost:9000/2015-03-31/functions/function/invocations" \
      -d '{
        "task": "new_typeform_customer",
        "customer": {
            "firstName": "Test",
            "lastName": "User",
            "email": "test12@sarahhamiltonface.com",
            "phone": "2345678022"
        },
        "typeform": {
            "type": "track",
            "event": "Anonymous Typeform Submission",
            "anonymousId": "asdf",
            "properties": {
                "Phone number": "+1234567890",
                "Great! Now which treatment'\''s are you most interested in?": "Skin Tightening,Wrinkle Reduction,Skin Clarity/Texture Improvements,Tattoo Removal",
                "First name": "Test",
                "Email": "test@sarahhamiltonface.com",
                "WELCOME!\n\nFirst off we'\''d love to know which Sarah Hamilton Face location you'\''re closest to?": "Liberty Lake, Washington",
                "Last name": "User",
                "Alright, what'\''s the best time for our team to reach out to you?": "Afternoon",
                "WELCOME!\n\nWhich location is closest to you?": "Liberty Lake, Washington",
                "Great! Now what types of treatment'\''s are you most interested in?": "Wrinkle Reduction,Skin Clarity/Texture Improvements"
            }
        },
        "source_key": "FBGJaePMD4KZGveRHkizE2sViDpvtdF6",
        "callback_object": "https://985d-50-37-160-145.ngrok-free.app"
    }'
echo ""

read -n 1 -s -r -p "Press any key to continue"

docker-compose down

docker ps -a