# Serverless 3CX Scraper

When starting a new project copy `.env.example` to `.env` and fill in the required values.


# How to push to Azure

1. Install the Azure CLI
2. Run `az login`
3. Run `az_acr_login.sh` to login to the Azure Container Registry
4. Run `build.sh && push.sh` to build and push the image to the Azure Container Registry
5. (Optional) Run `az_job_delete.sh` to delete the existing job
6. (Optional) Run `az_register_provider.sh` to register the provider if it hasn't been registered yet
   7. Run `az_job_create.sh` to create a new job
   *Note* This will securely add the environment variables to the job from .env file. So make sure to add the required environment variables to the .env file before running this command.