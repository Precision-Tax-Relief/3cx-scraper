#!/bin/bash

# If you get an registration error when creating a container, run this.
echo "Registering Microsoft.ContainerInstance provider..."
az provider register --namespace Microsoft.ContainerInstance

