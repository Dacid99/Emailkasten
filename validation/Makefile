lint: pylintrc
	pylint $< ../Emailkasten

stronglint: pylintrc_strong
	pylint $< ../Emailkasten

check: mypy.ini
	mypy --config-file $< Emailkasten/