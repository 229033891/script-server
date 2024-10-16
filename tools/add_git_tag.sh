#!/usr/bin/env bash

set -e

# 检查环境变量
REQUIRED_VARS=("TRAVIS_BRANCH" "OWNER" "GITHUB_TOKEN" "TRAVIS_REPO_SLUG")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: Environment variable '$var' is not set"
        exit 1
    fi
done

# 配置远程仓库
REMOTE_URL="https://${OWNER}:${GITHUB_TOKEN}@github.com/${TRAVIS_REPO_SLUG}.git"
git remote add gh "$REMOTE_URL"

# 根据分支设置标签
if [ "$TRAVIS_BRANCH" == "master" ]; then
    export NEW_GIT_TAG='dev'
    git tag -d 'dev' || true
    git push --delete gh 'dev' || true

elif [ "$TRAVIS_BRANCH" == "stable" ]; then
    if unzip -qc build/script-server.zip version.txt &>/dev/null; then
        version=$(unzip -qc build/script-server.zip version.txt)
        export NEW_GIT_TAG="$version"
    else
        echo "Error: Failed to extract version.txt from build/script-server.zip"
        exit 1
    fi
fi

# 检查是否需要打标签
if [ -z "$NEW_GIT_TAG" ]; then
    echo "Skipping tagging of branch '$TRAVIS_BRANCH'"
else
    git config --local user.name '229033891'
    git config --local user.email '229033891@qq.com'
    git tag -f "$NEW_GIT_TAG"
    git push -f gh "$NEW_GIT_TAG"
fi

# 清理远程仓库配置
git remote remove gh
