#!/bin/bash
# POC-DA-1: GCP Environment Setup Script
# RisenOne Fire Risk AI POC

set -e  # Exit on any error

echo "🚀 POC-DA-1: GCP Environment Setup for Fire Risk AI POC"
echo "============================================================"

# Check if we're in the right directory
if [ ! -f "deployment/poc_gcp_setup.py" ]; then
    echo "❌ Error: Must run from project root directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected files: deployment/poc_gcp_setup.py"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed"
    exit 1
fi

# Install POC requirements
echo "📦 Installing POC requirements..."
pip3 install -r deployment/requirements-poc.txt

# Check for GCP credentials
if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ] && [ ! -f "$HOME/.config/gcloud/application_default_credentials.json" ]; then
    echo "⚠️  Warning: No GCP credentials detected"
    echo "   Please run: gcloud auth application-default login"
    echo "   Or set GOOGLE_APPLICATION_CREDENTIALS environment variable"
    read -p "   Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get GCP project ID
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo "🔧 GCP Project Configuration"
    read -p "Enter your GCP Project ID: " PROJECT_ID
    if [ -z "$PROJECT_ID" ]; then
        echo "❌ Error: GCP Project ID is required"
        exit 1
    fi
    export GOOGLE_CLOUD_PROJECT="$PROJECT_ID"
else
    PROJECT_ID="$GOOGLE_CLOUD_PROJECT"
fi

echo "📋 Using GCP Project: $PROJECT_ID"

# Ask about fire data loading
echo ""
read -p "🔥 Load client fire data to BigQuery? (Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    LOAD_DATA_FLAG=""
else
    LOAD_DATA_FLAG="--load_fire_data"
fi

# Run the POC setup
echo ""
echo "🔧 Running POC-DA-1 setup..."
echo "   This may take several minutes..."
echo ""

cd deployment
python3 poc_gcp_setup.py \
    --project_id="$PROJECT_ID" \
    --setup_all \
    $LOAD_DATA_FLAG

# Check exit status
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 POC-DA-1 setup completed successfully!"
    echo ""
    echo "📋 Next Steps:"
    echo "   1. Review the generated .env.poc file in agent/"
    echo "   2. Test the setup: python3 poc_gcp_setup.py --validate_setup --project_id=$PROJECT_ID"
    echo "   3. Proceed with POC-DA-2: Geographic Data Foundation"
    echo ""
    echo "🔗 Useful Commands:"
    echo "   • Test APIs: python3 poc_gcp_setup.py --test_apis --project_id=$PROJECT_ID"
    echo "   • Load data: python3 poc_gcp_setup.py --load_fire_data --project_id=$PROJECT_ID"
    echo "   • Validate: python3 poc_gcp_setup.py --validate_setup --project_id=$PROJECT_ID"
else
    echo ""
    echo "❌ POC-DA-1 setup failed!"
    echo "   Check the error messages above and retry"
    echo "   For help, review the logs or run with --validate_setup"
    exit 1
fi 