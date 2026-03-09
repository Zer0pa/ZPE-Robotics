.PHONY: import-sanity portability-lint

import-sanity:
	python3 -m compileall src scripts tests

portability-lint:
	@if rg -n --no-heading -S '/Users/[A-Za-z0-9._ -]+|[A-Za-z]:\\\\' \
		README.md AUDITOR_PLAYBOOK.md PUBLIC_AUDIT_LIMITS.md CHANGELOG.md \
		CODE_OF_CONDUCT.md CONTRIBUTING.md SECURITY.md SUPPORT.md \
		docs proofs/runbooks scripts src tests \
		-g '*.md' -g '*.py' -g '*.toml' -g '*.yml' -g '*.yaml'; then \
		echo 'portability-lint: FAIL'; \
		exit 1; \
	else \
		echo 'portability-lint: PASS'; \
	fi
