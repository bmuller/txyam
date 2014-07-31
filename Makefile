PYDOCTOR=pydoctor

docs:
	$(PYDOCTOR) --make-html --html-output apidoc --add-package txyam --project-name=txyam --project-url=http://github.com/txyam --html-use-sorttable --html-use-splitlinks --html-shorten-lists 

lint:
	pep8 --ignore=E303 --max-line-length=120 ./txyam
	find ./txyam -name '*.py' | xargs pyflakes

test:
	trial txyam

install:
	python setup.py install
