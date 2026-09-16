# Sample queries

Each block is one `python3 -m querydesk` command. Classic weights, cosine,
`N = 18` unless noted.

## Hits

```bash
python3 -m querydesk rank "white whale pequod ahab"
python3 -m querydesk explain "white whale pequod ahab"

python3 -m querydesk rank "gryphon dormouse duchess hatter"
python3 -m querydesk rank "knightley hartfield harriet weston"
python3 -m querydesk rank "thel lyca lamb"
python3 -m querydesk rank "thane heath banquo witches"
python3 -m querydesk rank "leaves of grass"
python3 -m querydesk rank "paradise lost satan eden"
python3 -m querydesk rank "father brown flambeau"
python3 -m querydesk rank "anne elliot kellynch"
python3 -m querydesk rank "buster brown"
python3 -m querydesk rank "caesar brutus cassius"
python3 -m querydesk rank "queequeg stubb starbuck pequod"
```

## Gold `top` (reads `output/tfidf/`)

```bash
python3 -m querydesk top --doc carroll-alice.txt --n 12
python3 -m querydesk top --doc shakespeare-macbeth.txt --n 12
python3 -m querydesk top --doc melville-moby_dick.txt --n 12
python3 -m querydesk top --doc blake-poems.txt --n 12
```

## Variants

```bash
python3 -m querydesk compare "double toil trouble heath" --variants classic,smooth,bm25
python3 -m querydesk compare "the and of" --variants classic,smooth
```

## Field notes

```bash
python3 -m querydesk field-notes --query "cairn moraine icefall"
python3 -m querydesk field-notes --query "chase quoins tympan"
python3 -m querydesk field-notes --query "stilling well datum"
python3 -m querydesk field-notes --query "voucher silica blotters"
```
