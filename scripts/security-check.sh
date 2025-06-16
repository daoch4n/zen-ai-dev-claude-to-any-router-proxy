#!/bin/bash

# Security Check Script for Claude Code Proxy
# Run this before git commits to detect sensitive data

echo "🔒 Running pre-commit security scan..."
echo

# Only check files that would be committed (exclude gitignored files)
echo "1. Checking for OpenRouter API keys in tracked files..."
if git ls-files | xargs grep -l "sk-or-v1-[a-zA-Z0-9]\{50,\}" 2>/dev/null | xargs grep "sk-or-v1-[a-zA-Z0-9]\{50,\}" | grep -v "your-actual-openrouter-api-key-here"; then
    echo "❌ REAL OpenRouter API keys detected in tracked files!"
    exit 1
fi

echo "2. Checking for Databricks tokens in tracked files..."
if git ls-files | xargs grep -l "dapi[a-zA-Z0-9]\{20,\}" 2>/dev/null | xargs grep "dapi[a-zA-Z0-9]\{20,\}" | grep -v "dapi.*example\|dapi.*placeholder\|dapi1234567890"; then
    echo "❌ REAL Databricks tokens detected in tracked files!"
    exit 1
fi

echo "3. Checking for Anthropic API keys in tracked files..."
if git ls-files | xargs grep "sk-ant-[a-zA-Z0-9]\{30,\}" 2>/dev/null; then
    echo "❌ Anthropic API keys detected in tracked files!"
    exit 1
fi

echo "4. Checking for other sensitive patterns in tracked files..."
if git ls-files | xargs grep -E "(password|secret|private_key)=[a-zA-Z0-9]{8,}" 2>/dev/null | grep -v "getenv\|environ"; then
    echo "❌ Hardcoded secrets detected in tracked files!"
    exit 1
fi

echo "✅ Security scan passed - no sensitive data detected in tracked files"
echo "�� Safe to commit!" 