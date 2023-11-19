import tempfile
import boto3
import os
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

s3_client = boto3.client('s3')
ses_client = boto3.client('ses')


class InvalidFileHandler:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(InvalidFileHandler, cls).__new__(cls)
            # Attributes specific to this class
            cls._instance.error_files = []
            cls._instance.error_data = []
            cls._instance.dir_name = None
            cls._instance.initialized = False
        return cls._instance

    def __init__(self, bucket_name=None, region=None, sender=None, receiver=None, logger=None):
        if not hasattr(self, 'initialized') or not self.initialized:
            if not all([bucket_name, region, sender, receiver]):
                raise Exception("Must provide bucket_name, region, sender, and receiver on first initialization")
            self.error_files = []
            self.error_data = []
            self.bucket_name = bucket_name
            self.region = region
            self.sender = sender
            self.receiver = receiver
            self.logger = logger
            self.initialized = True

    def add_error(self, file_name, error_detail):
        self._upload_file(file_name)
        self.error_files.append(file_name)
        self.error_data.append(str(error_detail))

    def get_errors(self):
        return list(zip(self.error_files, self.error_data))

    def has_errors(self):
        num_errors = len(self.error_files)
        if num_errors > 0:
            self._upload_details()
            link = self._get_aws_link()
            self._send_email(link)
        return num_errors > 0

    def error_count(self):
        return len(self.error_files)

    def clear_errors(self):
        self.error_files.clear()
        self.error_data.clear()

    def _get_dir_name(self):
        if self.dir_name is None:
            self.dir_name = str(uuid.uuid4())

    def _get_aws_link(self):
        if self.dir_name is None:
            raise Exception("Must upload a file first")
        return f"https://{self.bucket_name}.s3.{self.receiver}.amazonaws.com/{self.dir_name}"

    def _upload_file(self, file_path, file_name=None):
        file_name = file_name or os.path.basename(file_path)
        s3_path = f'{self._get_dir_name()}/{file_name}'
        s3_client.upload_file(file_path, self.bucket_name, s3_path)
        if self.logger:
            self.logger.debug(f'Uploaded {file_name} to {s3_path}')

    def _upload_details(self):
        with tempfile.NamedTemporaryFile() as tmp:
            for file_name, error_detail in self.get_errors():
                tmp.write(f'{file_name}\n{error_detail}\n\n\n'.encode())
            tmp.flush()
            tmp.seek(0)
            self._upload_file(tmp.name, 'error_details.txt')

    def _send_email(self, link):
        subject = 'Booker Export has invalid files'
        body = f"Here is the link to the directory on S3: {link}"

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = self.receiver
        msg.attach(MIMEText(body, 'plain'))

        ses_client.send_raw_email(
            Source=self.sender,
            Destinations=[
                self.receiver
            ],
            RawMessage={
                'Data': msg.as_string(),
            }
        )
        self.logger.debug(f'Sent email to {self.receiver}')

