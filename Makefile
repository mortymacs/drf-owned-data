PYTHON ?= python3
PIP ?= pip3
VENV ?= $(PYTHON) -m venv

PACKAGE_DIR ?= dist
PACKAGE_FLAGS ?= sdist --dist-dir $(PACKAGE_DIR)

TEST_ENV_DIR ?= "test/.test-venv"

# Prepare test environment.
@PHONY: test-env
.ONESHELL:
test-env:
	if [ ! -d $(TEST_ENV_DIR) ]; then
		rm -rf $(TEST_ENV_DIR)
	fi
	$(VENV) $(TEST_ENV_DIR)
	$(PIP) install -r requirements-dev.txt

# Create a Python pacakge.
@PHONY: package
package:
	$(PYTHON) setup.py $(PACKAGE_FLAGS)

# Run integration tests.
@PHONY: test-integration
.ONESHELL:
test-integration: cleanup test-env package
	source $(TEST_ENV_DIR)/bin/activate
	$(PIP) install $(PACKAGE_DIR)/* -r requirements-dev.txt
	# Test DRF 'blog' project.
	cd test/integration/drf/blog
	./manage.py test

# Cleanup whatever it has built or generated.
@PHONY: cleanup
cleanup:
	rm -rf *.egg-info $(PACKAGE_DIR) $(TEST_ENV_DIR)

