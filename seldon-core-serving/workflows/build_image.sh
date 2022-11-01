#!/bin/bash -e

registry="docker.io"

echo "Login ${registry}"

docker login --username "${docker_username}" --password "${docker_password}" "${registry}"

component_name=$1
image_name="${docker_username}/${component_name}"
image_tag="v0.0.1"

full_image_name="${registry}/${image_name}:${image_tag}"

echo "MOVE TO $(pwd)"
cd "$(dirname "$0")"
cd "components_source/${component_name}/"

echo "Build: ${full_image_name}"
docker build -t "${full_image_name}" .

# echo "Push: ${full_image_name}"
# docker push "$full_image_name"

docker images --format="{{.Digest}}" "${full_image_name}"
