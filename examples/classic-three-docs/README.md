# Three-sentence TF-IDF example

This folder is the fully worked example in
`docs/06-hand-worked-example.md`.

```
cat_mat.txt   the cat sat on the mat
dog_log.txt   the dog sat on the log
friends.txt   cats and dogs are friends
```

Run it:

```bash
python3 examples/tfidf_toy.py --corpus examples/classic-three-docs
```

`cat` and `mat` tie at the top of the first document. `the` still
scores, because it is missing from `friends.txt`, so its IDF is
`ln(3/2)` rather than 0. Every token in `friends.txt` is unique to that
file, so those five terms tie.
