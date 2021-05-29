.PHONY: test
test: pep8
	python runtests.py

.PHONY: travis
travis:
	pip install -r requirements.txt requirements_test.txt
	export OPPS_TRAVIS=True
	python setup.py develop

.PHONY: install
install:
	pip install -r requirements.txt requirements_test.txt

.PHONY: pep8
pep8:
	@flake8 . --ignore=E501,F403,E126,E127,E128,E303 --exclude=migrations

.PHONY: sdist
sdist: test
	@python setup.py sdist upload

.PHONY: clean
clean:
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;

.PHONY: makemessages
makemessages:
	echo "making messages";\
	cd opps/ganalytics;\
	django-admin.py makemessages -l en_US;\
	cd ../../;\

.PHONY: compilemessages
compilemessages:
	echo "compiling messages";\
	cd opps/ganalytics;\
	django-admin.py compilemessages;\
	cd ../../;\
