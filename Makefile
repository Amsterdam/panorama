all: requirements.txt requirements_test.txt

requirements.txt: requirements_common.in requirements_prod.in
	pip-compile -v --output-file="$@" $^

requirements_test.txt: requirements_common.in requirements_test.in
	pip-compile -v --output-file="$@" $^
