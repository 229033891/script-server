#!/usr/bin/env bash

set -e

# 检查必要的环境变量
REQUIRED_VARS=("DOCKER_USER" "DOCKER_PASSWORD" "TRAVIS_BRANCH")
for var in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!var}" ]; then
    echo "Error: Environment variable '$var' is not set"
    exit 1
  fi
done

IMAGE_NAME='bugy/script-server'

# 解压缩构建文件
if ! unzip -o build/script-server.zip -d build/script-server; then
  echo "Error: Failed to unzip build/script-server.zip"
  exit 1
fi

# 根据分支设置 Docker 标签
case "$TRAVIS_BRANCH" in
  stable)
    DOCKER_TAG='latest'
    ;;
  master)
    DOCKER_TAG='dev'
    ;;
  *)
    DOCKER_TAG="$TRAVIS_BRANCH"
    ;;
esac

# 启动 QEMU 模拟器
if ! docker run --rm --privileged multiarch/qemu-user-static --reset -p yes; then
  echo "Error: Failed to start QEMU emulator"
  exit 1
fi

# 登录 Docker Hub
if ! echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USER" --password-stdin; then
  echo "Error: Failed to login to Docker Hub"
  exit 1
fi

# 设置额外的 Docker 标签参数
ADDITIONAL_TAG_ARG=""
if [ ! -z "$NEW_GIT_TAG" ]; then
  ADDITIONAL_TAG_ARG="-t $IMAGE_NAME:$NEW_GIT_TAG"
fi

# 创建并使用 buildx 构建器
if ! docker buildx create --use; then
  echo "Error: Failed to create buildx builder"
  exit 1
fi

# 构建并推送 Docker 镜像
if ! docker buildx build --platform linux/amd64,linux/arm64 --push -f tools/Dockerfile \
  -t "$IMAGE_NAME":"$DOCKER_TAG" \
  $ADDITIONAL_TAG_ARG \
  .; then
  echo "Error: Failed to build and push Docker image"
  exit 1
fi

echo "Docker image built and pushed successfully: $IMAGE_NAME:$DOCKER_TAG"
if [ ! -z "$NEW_GIT_TAG" ]; then
  echo "Additional tag: $IMAGE_NAME:$NEW_GIT_TAG"
fi
