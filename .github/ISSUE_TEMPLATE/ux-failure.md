---
name: UX Testing Failure
about: Automated UX test failure report
title: "[UX] "
labels: bug, ux-testing
assignees: ''
---

## Automated UX Test Failure

The automated UX testing workflow has detected issues that need attention.

### Workflow Run
- **Run ID**: {{ github.run_id }}
- **Triggered by**: {{ github.event_name }}
- **Branch**: {{ github.ref }}

### Common Issues to Check

1. **Missing Pages (404 errors)**
   - Verify all navigation links point to existing pages
   - Check that all required pages are created

2. **Broken Links**
   - Check for typos in href attributes
   - Verify external links are still valid

3. **Content Integrity**
   - Remove any fake testimonials
   - Replace hardcoded statistics with user data

4. **Auth UI**
   - Ensure login/logout buttons work
   - Verify user menu appears after sign in
   - Check that auth-dependent elements toggle correctly

### How to Debug

1. Review the workflow run logs
2. Run locally: `bundle exec jekyll serve`
3. Test all navigation links manually
4. Sign in and verify auth state changes

### Fix Priority

- 🔴 **Critical**: 404 errors, broken auth
- 🟡 **High**: Content integrity issues
- 🟢 **Medium**: Minor UI inconsistencies
