#!/bin/bash
# Demo Script for PythonParagon CLI Application
# This script demonstrates the various commands available

echo "=========================================="
echo "  PythonParagon CLI Demo"
echo "=========================================="
echo ""

# Show welcome screen
echo "1. Welcome Screen:"
python main.py
echo ""
read -p "Press Enter to continue..."

# Show info
echo ""
echo "2. Application Info:"
python main.py info
echo ""
read -p "Press Enter to continue..."

# List all commands
echo ""
echo "3. List All Commands:"
python main.py list-commands
echo ""
read -p "Press Enter to continue..."

# System Commands
echo ""
echo "=========================================="
echo "  System Commands"
echo "=========================================="
echo ""

echo "4. Memory Usage:"
python main.py system memory
echo ""
read -p "Press Enter to continue..."

echo ""
echo "5. CPU Monitoring (3 readings):"
python main.py system cpu --count 3 --interval 1
echo ""
read -p "Press Enter to continue..."

echo ""
echo "6. Top 10 Processes by Memory:"
python main.py system processes --limit 10 --sort-by memory
echo ""
read -p "Press Enter to continue..."

echo ""
echo "7. Disk Usage:"
python main.py system disk
echo ""
read -p "Press Enter to continue..."

# File Lab Commands
echo ""
echo "=========================================="
echo "  File Lab Commands"
echo "=========================================="
echo ""

echo "8. Directory Tree (max depth 2):"
python main.py filelab tree . --max-depth 2
echo ""
read -p "Press Enter to continue..."

echo ""
echo "9. File Metadata:"
python main.py filelab metadata .
echo ""
read -p "Press Enter to continue..."

echo ""
echo "10. Search Python Files:"
python main.py filelab search . --extension .py
echo ""
read -p "Press Enter to continue..."

# Utility Commands
echo ""
echo "=========================================="
echo "  Utility Commands"
echo "=========================================="
echo ""

echo "11. Generate Secure Passwords:"
python main.py utils password --length 20 --count 5
echo ""
read -p "Press Enter to continue..."

echo ""
echo "12. Generate UUIDs:"
python main.py utils uuid --count 5 --version 4
echo ""
read -p "Press Enter to continue..."

echo ""
echo "13. Hash Text (SHA256):"
python main.py utils hash "PythonParagon" --algorithm sha256
echo ""
read -p "Press Enter to continue..."

echo ""
echo "14. Base64 Encoding:"
python main.py utils base64 "Hello, PythonParagon!"
echo ""
read -p "Press Enter to continue..."

echo ""
echo "15. Base64 Decoding:"
python main.py utils base64 "SGVsbG8sIFB5dGhvblBhcmFnb24h" --decode
echo ""
read -p "Press Enter to continue..."

echo ""
echo "16. Render Markdown:"
python main.py utils markdown README.md
echo ""
read -p "Press Enter to continue..."

# Network Commands (some may fail without internet)
echo ""
echo "=========================================="
echo "  Network Commands"
echo "=========================================="
echo ""

echo "17. Get Public IP (may fail without internet):"
python main.py network ip || echo "Failed: No internet connection"
echo ""
read -p "Press Enter to continue..."

echo ""
echo "=========================================="
echo "  Demo Complete!"
echo "=========================================="
echo ""
echo "Explore more commands with:"
echo "  python main.py --help"
echo "  python main.py [CATEGORY] --help"
echo "  python main.py [CATEGORY] [COMMAND] --help"
echo ""
