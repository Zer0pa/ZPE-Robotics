# Trusted Publishing -- Operator Steps

The GitHub workflow side is aligned for OIDC publishing. The remaining steps are on the PyPI web UI:

1. Go to https://pypi.org/manage/project/zpe-motion-kernel/settings/publishing/
2. Click "Add a new publisher"
3. Select "GitHub Actions"
4. Fill in:
   - Owner: Zer0pa
   - Repository: ZPE-Robotics
   - Workflow filename: publish.yml
   - Environment name: pypi
5. Click "Add"

After completing these steps, the next `git tag vX.Y.Z && git push origin vX.Y.Z` will publish automatically without any token.
