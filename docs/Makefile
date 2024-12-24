# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

source: Makefile
	sphinx-apidoc -o source ../Emailkasten
	python3 ../manage.py graph_models -a -g -o $(SOURCEDIR)/db_graph.svg
	pydeps ../Emailkasten --max-bacon 2 -T svg -L ERROR --rankdir LR --no-show -o $(SOURCEDIR)/import_graph.svg

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

webview:
	python3 -m http.server --directory build/html
