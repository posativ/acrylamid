
SPHINXBUILD   = python run.py

.PHONY: help blog

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  blog       re-generate blog"

blog:
	$(SPHINXBUILD) output
