lint: pylintrc
	pylint --rcfile=$< ../Emailkasten | tee reports/pylint.txt

strictlint: pylintrc_strict
	pylint --rcfile=$< ../Emailkasten | tee reports/pylint_strict.txt

check: mypy.ini
	mypy --config-file $< ../Emailkasten/

clean:
	rm -f reports/* ../docs/mypy_report.html ../docs/*.svg
