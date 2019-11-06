# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build
HTMLDIR       = ..
HTMLDEVDIR    = ../dev/

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

github_release:
	@make html
	@rm -rf $(HTMLDIR)/_static/
	@rm -rf $(HTMLDIR)/_images/
	@rm -rf $(HTMLDIR)/.buildinfo
	@rm -rf $(HTMLDIR)/_sources/
	@rm -f $(HTMLDIR)/*.html
	@rm -f $(HTMLDIR)/objects.inv
	@rm -f $(HTMLDIR)/searchindex.js
	@cp -a $(BUILDDIR)/html/. $(HTMLDIR)
	@touch $(HTMLDIR)/.nojekyll
	@git add -A
	@git stash
	@git checkout gh-pages
	@git stash apply
	@git commit -m "Make Github release"
	@git commit push origin gh-pages

github_dev:
	@make html
	@rm -rf $(HTMLDEVDIR)/_static/
	@rm -rf $(HTMLDEVDIR)/_images/
	@rm -rf $(HTMLDEVDIR)/.buildinfo
	@rm -rf $(HTMLDEVDIR)/_sources/
	@rm -f $(HTMLDEVDIR)/*.html
	@rm -f $(HTMLDEVDIR)/objects.inv
	@rm -f $(HTMLDEVDIR)/searchindex.js
	@cp -a $(BUILDDIR)/html/. $(HTMLDEVDIR)
	@touch $(HTMLDEVDIR)/.nojekyll


# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
  
