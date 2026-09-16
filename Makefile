.PHONY: test demo bible alice voices

test:
	python3 -m unittest discover -s tests -v

demo:
	python3 -m shelf_units demo

bible:
	python3 -m shelf_units bible -k 5

alice:
	python3 -m shelf_units chapters carroll-alice -k 5

voices:
	python3 -m shelf_units voices shakespeare-macbeth -k 6
