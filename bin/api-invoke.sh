curl -X POST "https://dzfvb320ef.execute-api.us-west-2.amazonaws.com/development/booker" \
     -H "Content-Type: application/json" \
     -d '{
           "task": "create_customer",
           "customer": {
               "first_name": "John",
               "last_name": "Doe",
               "email": "john.doe@example.com",
               "phone": "1234567890"
           }
         }'

#     -H "x-api-key: zBlYh4HwPR5a0E1ttUxiS92O0PZHU2VD3xxZaKlu" \
