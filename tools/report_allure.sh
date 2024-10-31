#!/bin/bash

set -e

# 检查必要的环境变量
REQUIRED_VARS=("TRAVIS_BRANCH" "TRAVIS_BUILD_NUMBER" "TRAVIS_PULL_REQUEST" "TRAVIS_REPO_SLUG" "GITHUB_TOKEN")
for var in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!var}" ]; then
    echo "Error: Environment variable '$var' is not set"
    exit 1
  fi
done

# 同步测试报告到 S3
S3_BUCKET="script-server-tests"
S3_PATH="s3://${S3_BUCKET}/${TRAVIS_BRANCH}/${TRAVIS_BUILD_NUMBER}"
LOCAL_REPORT_PATH="/tmp/allure_report"

if aws s3 sync "$LOCAL_REPORT_PATH" "$S3_PATH"; then
  echo "Successfully uploaded test reports to S3."

  allure_url="https://${S3_BUCKET}.s3-us-west-2.amazonaws.com/${TRAVIS_BRANCH}/${TRAVIS_BUILD_NUMBER}/index.html"
  echo "Test results: $allure_url"

  # 如果是 Pull Request，则在 GitHub 上发布评论
  if [ "$TRAVIS_PULL_REQUEST" != "false" ]; then
    GITHUB_API_URL="https://api.github.com/repos/${TRAVIS_REPO_SLUG}/issues/${TRAVIS_PULL_REQUEST}/comments"
    COMMENT_BODY="{\"body\": \"Test results: $allure_url\"}"

    if curl -H "Authorization: token ${GITHUB_TOKEN}" -X POST -d "$COMMENT_BODY" "$GITHUB_API_URL"; then
      echo "Successfully posted comment to GitHub."
    else
      echo "Error: Failed to post comment to GitHub."
      exit 1
    fi
  fi
else
  echo "Error: Failed to upload test reports to S3."
  exit 1
fi
