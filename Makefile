.PHONY: demo top test compare compute

python := python3

demo:
	$(python) -m tfidf_toy demo

top:
	$(python) -m tfidf_toy top --input gutenberg --k 12

compare:
	$(python) -m tfidf_toy compare --input gutenberg austen-emma.txt austen-sense.txt --k 12

compute:
	$(python) -m tfidf_toy compute --input gutenberg --output output_py

test:
	$(python) -m unittest discover -s tests -v
