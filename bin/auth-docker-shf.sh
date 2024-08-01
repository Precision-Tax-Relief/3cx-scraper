#!/bin/bash
aws ecr get-login-password --region us-east-1 --profile shf | docker login --username AWS --password-stdin 281172820522.dkr.ecr.us-east-1.amazonaws.com
