# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| < main  | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

1. **Do NOT** create a public GitHub issue for security vulnerabilities
2. Email security concerns to the repository maintainers
3. Include as much detail as possible:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment**: Within 48 hours of your report
- **Initial Assessment**: Within 5 business days
- **Resolution Timeline**: Depends on severity, typically within 30 days
- **Credit**: We will credit reporters in release notes (unless you prefer anonymity)

## Security Best Practices

When using this action:

### Secrets Management
- Never commit secrets to the repository
- Use GitHub Secrets for sensitive values
- Rotate credentials regularly
- Use OIDC authentication when possible

### Terraform State
- Enable state file encryption
- Use remote state with locking
- Restrict access to state storage

### Azure Authentication
- Prefer OIDC over service principals
- Use least-privilege access
- Review and audit permissions regularly

### Workflow Security
- Pin action versions to specific SHAs
- Review workflow files for injection vulnerabilities
- Limit workflow permissions with `permissions` key

## Security Features

This action includes:

- **No secrets in logs**: Sensitive values are masked
- **Input validation**: All inputs are validated before use
- **Subprocess safety**: Commands are constructed safely
- **Dependency scanning**: Regular security updates for dependencies

## Dependency Updates

We monitor dependencies for security vulnerabilities using:
- Dependabot for automated updates
- GitHub Security Advisories
- pip-audit for Python packages

## Disclosure Policy

We follow a coordinated disclosure policy:

1. Reporter contacts us privately
2. We acknowledge and investigate
3. We develop and test a fix
4. We release the fix
5. We publicly disclose after patch is available

## Contact

For security concerns, please contact the repository maintainers through GitHub's private vulnerability reporting feature or via email to the organization administrators.
