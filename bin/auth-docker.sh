#!/bin/bash
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 515970055937.dkr.ecr.us-west-2.amazonaws.com