#!/bin/bash

# Cache Cleanup Script
# This script clears various application caches to free up disk space

echo "🧹 Starting cache cleanup..."
echo ""

# Function to calculate size before deletion
calculate_size() {
    du -sh "$1" 2>/dev/null | cut -f1 || echo "0"
}

# Chrome Cache
echo "📦 Cleaning Chrome cache..."
chrome_cache_size=$(calculate_size ~/.cache/google-chrome)
rm -rf ~/.cache/google-chrome/* 2>/dev/null
rm -rf ~/.config/google-chrome/Default/Cache 2>/dev/null
rm -rf ~/.config/google-chrome/Default/Code\ Cache 2>/dev/null
echo "   ✓ Chrome cache cleared ($chrome_cache_size)"

# VSCode C++ Tools Cache
echo "📦 Cleaning VSCode C++ Tools cache..."
cpptools_size=$(calculate_size ~/.cache/vscode-cpptools)
rm -rf ~/.cache/vscode-cpptools/* 2>/dev/null
echo "   ✓ VSCode C++ Tools cache cleared ($cpptools_size)"

# Tracker3 Cache
echo "📦 Cleaning Tracker3 cache..."
tracker_size=$(calculate_size ~/.cache/tracker3)
rm -rf ~/.cache/tracker3/* 2>/dev/null
echo "   ✓ Tracker3 cache cleared ($tracker_size)"

# Mesa Shader Cache
echo "📦 Cleaning Mesa shader cache..."
mesa_size=$(calculate_size ~/.cache/mesa_shader_cache)
rm -rf ~/.cache/mesa_shader_cache/* 2>/dev/null
echo "   ✓ Mesa shader cache cleared ($mesa_size)"

# npm Cache (if npm exists)
if command -v npm &> /dev/null; then
    echo "📦 Cleaning npm cache..."
    npm_size=$(calculate_size ~/.npm)
    npm cache clean --force 2>/dev/null
    echo "   ✓ npm cache cleared ($npm_size)"
else
    echo "📦 npm not found, skipping..."
fi

# Slack Cache
echo "📦 Cleaning Slack cache..."
slack_cache_size=$(calculate_size ~/.config/Slack/Cache)
slack_sw_size=$(calculate_size ~/.config/Slack/Service\ Worker/CacheStorage)
rm -rf ~/.config/Slack/Cache/* 2>/dev/null
rm -rf ~/.config/Slack/Service\ Worker/CacheStorage/* 2>/dev/null
rm -rf ~/.config/Slack/Code\ Cache/* 2>/dev/null
echo "   ✓ Slack cache cleared ($slack_cache_size + $slack_sw_size)"

# NVM Cache (if exists)
if [ -d ~/.nvm/.cache ]; then
    echo "📦 Cleaning NVM cache..."
    nvm_size=$(calculate_size ~/.nvm/.cache)
    rm -rf ~/.nvm/.cache 2>/dev/null
    echo "   ✓ NVM cache cleared ($nvm_size)"
else
    echo "📦 NVM cache not found, skipping..."
fi

echo ""
echo "✨ Cleanup complete!"
echo ""
echo "📊 Current disk usage:"
df -h ~ | tail -1 | awk '{print "   Used: " $3 " / " $2 " (" $5 ") | Available: " $4}'
