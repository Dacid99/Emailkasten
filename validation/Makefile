codelint: pylintrc_code
	pylint --rcfile=$< ../Emailkasten ../core/ ../api/ ../web/ | tee reports/pylint_code.ansi

docslint: pylintrc_docs
	pylint --rcfile=$< ../Emailkasten ../core/ ../api/ ../web/ ../test/ | tee reports/pylint_docs.ansi

stylelint: pylintrc_style
	pylint --rcfile=$< ../Emailkasten ../core/ ../api/ ../web/ ../test/ | tee reports/pylint_style.ansi

testlint: pylintrc_style
	pylint --rcfile=$< ../test/ | tee reports/pylint_test.ansi

check: mypy.ini
	mypy --config-file $< ../Emailkasten ../test/ ../core/ ../api/ ../web/

clean:
	rm -f reports/* ../docs/mypy_report.html ../docs/*.svg
