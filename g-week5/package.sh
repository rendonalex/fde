#!/bin/bash
# Package script for FDE ADR Pipeline
# Creates a clean zip file for distribution to coaches

echo "📦 Packaging FDE ADR Pipeline..."

# Set package name
PACKAGE_NAME="fde-adr-pipeline"
OUTPUT_FILE="${PACKAGE_NAME}.zip"

# Create temporary directory
TEMP_DIR="/tmp/${PACKAGE_NAME}"
rm -rf "${TEMP_DIR}"
mkdir -p "${TEMP_DIR}/g-week5"

echo "📋 Copying essential files..."

# Copy main directories
cp -r agents "${TEMP_DIR}/g-week5/"
cp -r workflow "${TEMP_DIR}/g-week5/"
cp -r mock-data "${TEMP_DIR}/g-week5/"
cp -r deliverables "${TEMP_DIR}/g-week5/"

# Copy test scripts
cp test_adr2.py "${TEMP_DIR}/g-week5/"
cp test_adr2_suite.py "${TEMP_DIR}/g-week5/"
cp test_single.py "${TEMP_DIR}/g-week5/"

# Copy documentation
cp README.md "${TEMP_DIR}/g-week5/"
cp QUICKSTART.md "${TEMP_DIR}/g-week5/"
cp AGENT_BUILD_SUMMARY.md "${TEMP_DIR}/g-week5/"
cp requirements.txt "${TEMP_DIR}/g-week5/"

echo "🧹 Cleaning unnecessary files..."

# Remove Python cache
find "${TEMP_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find "${TEMP_DIR}" -type f -name "*.pyc" -delete
find "${TEMP_DIR}" -type f -name ".DS_Store" -delete

# Remove result files
rm -f "${TEMP_DIR}/g-week5/test_adr2_results.json"
rm -f "${TEMP_DIR}/g-week5/workflow_results.json"
rm -f "${TEMP_DIR}/g-week5/results.json"

echo "📦 Creating zip archive..."

# Create zip file (excluding this script)
cd "${TEMP_DIR}" || exit
zip -r "${OUTPUT_FILE}" g-week5/ -x "*.git*" "*.idea*" "*.vscode*" > /dev/null

# Move to original directory
mv "${OUTPUT_FILE}" "${OLDPWD}/"
cd "${OLDPWD}" || exit

# Clean up temp directory
rm -rf "${TEMP_DIR}"

echo "✅ Package created: ${OUTPUT_FILE}"
echo ""
echo "📊 Package contents:"
unzip -l "${OUTPUT_FILE}" | grep -E "g-week5/(README|QUICKSTART|test_|workflow/|agents/|mock-data/)" | head -20
echo "   ... (full contents in zip file)"
echo ""
echo "📤 Ready to upload to shared drive!"
echo ""
echo "🚀 Coaches can run:"
echo "   1. unzip ${OUTPUT_FILE}"
echo "   2. cd g-week5"
echo "   3. pip install -r requirements.txt"
echo "   4. export ANTHROPIC_API_KEY='...'"
echo "   5. python3 test_adr2_suite.py"
