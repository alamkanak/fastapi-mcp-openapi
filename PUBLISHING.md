# PyPI Publishing Setup Guide

This document explains how to set up automated PyPI publishing for the `fastapi-mcp-openapi` library using GitHub Actions and PyPI's Trusted Publishing feature.

## Overview

The project uses GitHub Actions to automatically:
- ✅ Run tests on Python 3.12 and 3.13
- 🔨 Build distribution packages (wheel and source distribution)
- 🧪 Publish to TestPyPI on every push to `main` branch
- 🚀 Publish to PyPI on tagged releases (e.g., `v1.0.0`)
- 📝 Create GitHub releases with attached distribution files

## Setup Instructions

### 1. Configure PyPI Trusted Publishing

#### For PyPI (Production)

1. Go to [https://pypi.org/manage/account/publishing/](https://pypi.org/manage/account/publishing/)
2. Click "Add a new pending publisher"
3. Fill in the form:
   - **PyPI Project Name**: `fastapi-mcp-openapi`
   - **Owner**: Your GitHub username or organization name
   - **Repository name**: `fastapi-mcp-openapi`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`
4. Click "Add"

#### For TestPyPI (Testing)

1. Go to [https://test.pypi.org/manage/account/publishing/](https://test.pypi.org/manage/account/publishing/)
2. Click "Add a new pending publisher"
3. Fill in the same information as above, but use:
   - **Environment name**: `testpypi`
4. Click "Add"

> **Note**: You need separate accounts for PyPI and TestPyPI. If you don't have a TestPyPI account, create one at [https://test.pypi.org/account/register/](https://test.pypi.org/account/register/).

### 2. Configure GitHub Repository Environments

#### Set up PyPI Environment (Production)

1. Go to your GitHub repository settings
2. Click on "Environments" in the left sidebar
3. Click "New environment"
4. Name it `pypi`
5. **Important**: Enable "Required reviewers" and add yourself as a reviewer for security
6. Click "Configure environment"

#### Set up TestPyPI Environment (Testing)

1. Create another environment named `testpypi`
2. You can leave this without required reviewers since it's for testing

### 3. Workflow Files

The repository includes two GitHub Actions workflows:

#### `/.github/workflows/test.yml`
- Runs on every pull request and push to main
- Tests the code on Python 3.12 and 3.13
- Runs linting and formatting checks with Ruff
- Runs type checking with MyPy

#### `/.github/workflows/publish.yml`
- Runs tests first
- Builds distribution packages
- Publishes to TestPyPI on pushes to `main`
- Publishes to PyPI on tagged releases
- Creates GitHub releases with distribution files

## Usage

### Testing Changes

Every push to `main` will:
1. Run the test suite
2. If tests pass, publish to TestPyPI
3. You can test the TestPyPI version with:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ fastapi-mcp-openapi
   ```

### Creating a Release

To publish to PyPI:

1. **Update the version** in `pyproject.toml`:
   ```toml
   version = "1.0.0"  # Update this
   ```

2. **Commit and push** the version change:
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 1.0.0"
   git push origin main
   ```

3. **Create and push a tag**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

4. **Monitor the workflow**:
   - Go to the "Actions" tab in your GitHub repository
   - Watch the "Publish Python distribution to PyPI and TestPyPI" workflow
   - If configured correctly, it will require manual approval for the `pypi` environment

5. **Approve the deployment** (if you set up required reviewers):
   - Click on the workflow run
   - Click "Review deployments"
   - Select the `pypi` environment and click "Approve and deploy"

### Workflow Behavior

| Event | TestPyPI | PyPI | GitHub Release |
|-------|----------|------|----------------|
| Push to `main` | ✅ Published | ❌ No | ❌ No |
| Push tag `v*` | ❌ No | ✅ Published | ✅ Created |
| Pull Request | ❌ No | ❌ No | ❌ No |

## Security Features

- **Trusted Publishing**: No API tokens needed, uses OpenID Connect
- **Environment Protection**: Production deployments require manual approval
- **Automatic Attestations**: PEP 740-compatible attestations are generated automatically
- **Minimal Permissions**: Workflows only have necessary permissions

## Troubleshooting

### Common Issues

1. **"Trusted publisher not found"**
   - Ensure the PyPI trusted publisher is configured correctly
   - Check that the repository name, owner, workflow file, and environment name match exactly

2. **"Environment protection rules"**
   - Make sure you've set up the `pypi` environment in GitHub repository settings
   - If you enabled required reviewers, you need to manually approve the deployment

3. **"Package already exists"**
   - You cannot overwrite existing versions on PyPI
   - Increment the version number in `pyproject.toml`

4. **"Tests failing"**
   - The workflow will not publish if tests fail
   - Check the test output in the GitHub Actions logs

### Debugging

- View workflow logs in the "Actions" tab of your repository
- Test locally before pushing:
  ```bash
  # Run tests
  python -m pytest -v
  
  # Build package
  python -m build
  
  # Check package
  python -m twine check dist/*
  ```

## Manual Publishing (Backup)

If you need to publish manually:

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*
```

## Links

- [PyPI Trusted Publishing Documentation](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Python Packaging Guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
