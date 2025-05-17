# GitHub Pages Setup Guide

This guide explains how to enable GitHub Pages for the GXtract repository to automatically build and publish documentation.

## Prerequisites

1. The GXtract repository has been pushed to GitHub under the account (e.g., github.com/sascharo/gxtract)
2. Administrative access to the repository

## Steps to Enable GitHub Pages

1. **Push the GitHub Actions workflow file to the repository**
   
   The workflow file located at `.github/workflows/docs.yml` will automatically build the documentation when changes are pushed to the main branch.

2. **Set up GitHub Pages in the repository settings**

   a. Go to the repository on GitHub (e.g., https://github.com/sascharo/gxtract)
   b. Navigate to "Settings" (tab in the top menu)
   c. Scroll down to the "Pages" section in the left sidebar
   d. Under "Source", select "GitHub Actions"
   e. Save the settings

3. **Initial Documentation Build**

   a. Go to the "Actions" tab in the repository
   b. Find the "Build and Deploy Documentation" workflow
   c. Click "Run workflow" to manually trigger the first build
   d. Wait for the workflow to complete (this usually takes 1-3 minutes)

4. **Access the Documentation**

   After the workflow completes successfully, the documentation will be available at:
   https://sascharo.github.io/gxtract/

   The URL will also be displayed in the "deploy" job output in the GitHub Actions workflow.

## Troubleshooting

- If the workflow fails, check the build logs in the Actions tab for specific error messages
- Verify that the Sphinx configuration is correct and builds successfully locally
- Make sure all required dependencies are specified in the `pyproject.toml`
- Check the permissions settings in the repository if deployment errors can be seen

## Customizing the Documentation Site

- The appearance of the documentation can be customized by modifying the Sphinx configuration in `docs/sphinx/source/conf.py`
- The GitHub Pages site will automatically update whenever changes are pushed to the documentation source files

## Additional Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Sphinx Documentation](https://www.sphinx-doc.org/)
