.PHONY: test field-notes alice self-test rank

PYTHON ?= python3

test:
	$(PYTHON) -m unittest discover -s tests -v

self-test:
	$(PYTHON) -m querydesk self-test

field-notes:
	$(PYTHON) -m querydesk field-notes
	$(PYTHON) -m querydesk field-notes --query "chase quoins tympan"
	$(PYTHON) -m querydesk field-notes --query "stilling datum slack"
	$(PYTHON) -m querydesk field-notes --query "voucher blotters silica"

alice:
	$(PYTHON) -m querydesk top --doc carroll-alice.txt --n 12

rank:
	$(PYTHON) -m querydesk rank "white whale pequod ahab"
	$(PYTHON) -m querydesk explain "white whale pequod ahab"
