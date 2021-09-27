#
# The main Makefile for regression tests.
#

.PHONY: clean clean-tests docs docs-coverage help lint tests tests-coverage tests-timings

help:
	@echo "Use \`make <target>\`, where <target> is one of"
	@echo "  clean          -> clean all the generated files"
	@echo "  docs           -> generate the documentation"
	@echo "  docs-coverage  -> generate documentation coverage"
	@echo "  lint           -> check code style with flake8"
	@echo "  tests          -> run the tests"
	@echo "  tests-coverage -> obtain test coverage"
	@echo "  tests-timings  -> obtain test timings"

clean:
	@rm -rf .coverage coverage
	@rm -f logs/*.log
	@find . -name '__pycache__' -exec rm -rf {} +
	@find . -name '*.py[co]' -exec rm -f {} +
	@$(MAKE) -C docs clean

docs:
	@sphinx-apidoc -f -o docs/ regression_tests
	@$(MAKE) -C docs clean
	@$(MAKE) -C docs html

docs-coverage:
	@$(MAKE) -C docs coverage

lint:
	@flake8 \
		--jobs=auto \
		--max-line-length=100 \
		--ignore=E402,W504 \
		regression_tests tests *.py | \
		grep -v "tests/.*:[0-9]*:[0-9]*: E501 line too long .*" | \
		grep -v "regression_tests/parsers/c_parser/__init__.py:[0-9]*:[0-9]*: F401 'parse' imported but unused" \
		; true # Always end successfully because of the above greps.

tests:
	@nosetests tests \
		--processes=-1

tests-coverage:
	@nosetests tests \
		--with-coverage \
		--cover-package regression_tests \
		--cover-erase \
		--cover-html \
		--cover-html-dir coverage

tests-timings:
	@nosetests tests \
		--with-timer \
		--timer-ok=10ms \
		--timer-warning=50ms
