import boto3
import os
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import tempfile

s3_client = boto3.client('s3')
ses_client = boto3.client('ses')

AWS_REGION = 'us-west-2'  # change this to your region
BUCKET_NAME = 'booker-test'
SENDER_EMAIL = 'logan@rufsoft.com'
RECEIVER_EMAIL = 'logan@novacru.com'


def file_test():
    # 1. Create a new directory name (using a UUID for uniqueness)
    directory_name = str(uuid.uuid4())

    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(b'This is test data!')
        tmp.flush()
        tmp.seek(0)
        file_path = tmp.name
        file_name = os.path.basename(tmp.name)

        # 2. Upload your file to the directory in S3
        s3_path = os.path.join(directory_name, file_name)
        s3_client.upload_file(file_path, BUCKET_NAME, s3_path)

        # 3. Send an email with a link to the directory
        link = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{directory_name}/{file_name}"
    print(link)
    send_email(SENDER_EMAIL, RECEIVER_EMAIL, link)


def send_email(sender, recipient, link):
    subject = 'Your S3 Directory Link'
    body = f"Here is the link to your directory on S3: {link}"

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    msg.attach(MIMEText(body, 'plain'))

    response = ses_client.send_raw_email(
        Source=sender,
        Destinations=[
            recipient
        ],
        RawMessage={
            'Data': msg.as_string(),
        }
    )


if __name__ == "__main__":
    send_email(SENDER_EMAIL, RECEIVER_EMAIL, 'https://www.google.com')
    # file_test()