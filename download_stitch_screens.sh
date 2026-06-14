#!/bin/bash

# TalentMind AI - Stitch Asset Downloader
# Run this in Git Bash, WSL, or a Linux/macOS terminal

PROJECT_ID="17873559004469996604"

# TODO: Replace this with the actual base URL for the Stitch export API
BASE_URL="https://api.your-stitch-domain.com/v1/projects"

# Map screen names to their Stitch IDs
declare -A SCREENS=(
    ["dashboard"]="dafaaeb59401404fb076603b1084e0c0"
    ["candidate_explorer"]="f71d90e2844243cfb95b46785283fbcb"
    ["ranking_intelligence"]="238c83816e12420b85d2026cf8256a00"
    ["candidate_details"]="d2361a0d83ea49b2b5ba6880436e58dc"
    ["skill_gap_intelligence"]="7d119ba061a949e198718a0441cfceec"
    ["settings"]="42e09f980af34df89c761fee2737161a"
)

# Ensure target directories exist
mkdir -p frontend_screens/images

echo "Starting download for Project ID: $PROJECT_ID..."

for name in "${!SCREENS[@]}"; do
    screen_id=${SCREENS[$name]}
    echo "Fetching $name (ID: $screen_id)..."
    
    # Download HTML/Code
    # Adjust the endpoint suffix (/code, /download, etc.) based on the Stitch API documentation
    curl -L -s "$BASE_URL/$PROJECT_ID/screens/$screen_id/code" -o "frontend_screens/${name}.html"
    
    # Download Image Previews
    curl -L -s "$BASE_URL/$PROJECT_ID/screens/$screen_id/image" -o "frontend_screens/images/${name}.png"
done

echo "All screens successfully downloaded into d:\TalentMindAI\frontend_screens\"