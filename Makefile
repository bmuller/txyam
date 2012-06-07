PYDOCTOR=pydoctor

docs:
	$(PYDOCTOR) --make-html --html-output apidoc --add-package txyam --project-name=txyam --project-url=http://github.com/txyam --html-use-sorttable --html-use-splitlinks --html-shorten-lists 

test:
	trial txyam

install:
	python setup.py install
