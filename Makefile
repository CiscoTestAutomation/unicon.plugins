# Variables
PKG_NAME      = unicon.plugins
BUILD_DIR     = $(shell pwd)/__build__
DIST_DIR      = $(BUILD_DIR)/dist
SOURCEDIR     = .
PROD_USER     = pyadm@pyats-ci
PROD_PKGS     = /auto/pyats/packages/cisco-shared
PYTHON        = python
TESTCMD       = runAll --path=tests/
BUILD_CMD     = $(PYTHON) setup.py bdist_wheel --dist-dir=$(DIST_DIR)
PYPIREPO      = pypitest


DEPENDENCIES = robotframework pyyaml dill coverage Sphinx \
			   sphinxcontrib-napoleon sphinxcontrib-mockautodoc \
			   sphinx-rtd-theme asyncssh


.PHONY: clean package distribute develop undevelop help devnet\
        docs test install_build_deps uninstall_build_deps

help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo ""
	@echo "package               Build the package"
	@echo "test                  Test the package"
	@echo "distribute            Distribute the package to internal Cisco PyPi server"
	@echo "clean                 Remove build artifacts"
	@echo "develop               Build and install development package"
	@echo "undevelop             Uninstall development package"
	@echo "docs                  Build Sphinx documentation for this package"
	@echo "install_build_deps    does nothing - just following pyATS pkg standard"
	@echo "uninstall_build_deps  does nothing - just following pyATS pkg standard"
	@echo ""

install_build_deps:
	@pip install --upgrade pip setuptools wheel

uninstall_build_deps:
	@echo ""

html: docs

docs:
	@echo ""
	@echo "--------------------------------------------------------------------"
	@echo "Building $(PKG_NAME) documentation for preview: $@"
	@echo ""

	python docs/gen_dialogs_rst.py > docs/user_guide/services/service_dialogs.rst
	sphinx-build -b html -c docs -d ./__build__/documentation/doctrees docs/ ./__build__/documentation/html

	@echo "Completed building docs for preview."
	@echo ""


test:
	@$(TESTCMD)

package:
	@echo ""
	@echo "--------------------------------------------------------------------"
	@echo "Building $(PKG_NAME) distributable: $@"
	@echo ""

	$(BUILD_CMD)

	@echo ""
	@echo "Completed building: $@"
	@echo ""

develop:
	@echo ""
	@echo "--------------------------------------------------------------------"
	@echo "Building and installing $(PKG_NAME) development distributable: $@"
	@echo ""
	@pip uninstall -y $(PKG_NAME)
	@pip install $(DEPENDENCIES)
	@$(PYTHON) setup.py develop --no-deps
	@echo ""
	@echo "Completed building and installing: $@"
	@echo ""

undevelop:
	@echo ""
	@echo "--------------------------------------------------------------------"
	@echo "Uninstalling $(PKG_NAME) development distributable: $@"
	@echo ""

	@$(PYTHON) setup.py develop --no-deps -q --uninstall

	@echo ""
	@echo "Completed uninstalling: $@"
	@echo ""

clean:
	@echo ""
	@echo "--------------------------------------------------------------------"
	@echo "Removing make directory: $(BUILD_DIR)"
	@rm -rf $(BUILD_DIR) $(DIST_DIR)
	@echo ""
	@echo "Removing build artifacts ..."
	@$(PYTHON) setup.py clean
	@echo ""
	@echo "Done."
	@echo ""

distribute:
	@echo ""
	@echo "--------------------------------------------------------------------"
	@echo "Copying all distributable to $(PROD_PKGS)"
	@test -d $(DIST_DIR) || { echo "Nothing to distribute! Exiting..."; exit 1; }
	@ssh -q $(PROD_USER) 'test -e $(PROD_PKGS)/$(PKG_NAME) || mkdir $(PROD_PKGS)/$(PKG_NAME)'
	@scp $(DIST_DIR)/* $(PROD_USER):$(PROD_PKGS)/$(PKG_NAME)/
	@echo ""
	@echo "Done."
	@echo ""
