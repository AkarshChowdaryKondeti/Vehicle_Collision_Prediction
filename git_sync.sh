#!/bin/bash

git pull origin main
git add .
read -p "Commit message: " message
git commit -m "$message"
git push origin main
