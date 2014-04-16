
PYTHON=`which python`
DESTDIR=/
CURDIR=$(shell pwd)
PROJECT=levitas
VERSION="0.0.1"

all:
	@echo "make source - Create source package"
	@echo "make install - Install on local system"
	#@echo "make rpm - Generate a rpm package"
	@echo "make deb - Generate a deb package"
	@echo "make doc - Generate API documentation"
	@echo "make clean - Get rid of scratch and byte files"

source:
	cd src; $(PYTHON) setup.py sdist $(COMPILE)

install:
	cd src; $(PYTHON) setup.py install --root $(DESTDIR) $(COMPILE)
	make clean

#rpm:
#	cd src; $(PYTHON) setup.py bdist_rpm #--post-install=rpm/postinstall --pre-uninstall=rpm/preuninstall

deb:
	dpkg-buildpackage -i -I -us -uc -rfakeroot
	fakeroot debian/rules clean
	make clean

test:
	cd src; $(PYTHON) test.py
	
doc:
	#cd src; epydoc -v --html --debug --no-sourcecode --graph all --output=../api $(PROJECT)
	cd src; epydoc -v --html --output=../api $(PROJECT)
	
clean:
	cd src; $(PYTHON) setup.py clean
	cd src; rm -rf build/ MANIFEST dist/
	rm -rf api
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name '__pycache__' -delete
