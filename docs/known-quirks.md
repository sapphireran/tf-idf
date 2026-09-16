# Known quirks

This is a 2012 teaching toy. The quirks below are part of the lesson: a ranking is only as honest as the tokenizer, the collection size, and the sort you use to read it.

## Tokenization is a blunt regex

From `tf-idf-values.pl`:

```perl
$txt =~ s/[\h\v]+/ /g;       # collapse whitespace
$txt =~ tr/[A-Z]/[a-z]/;     # lowercase (see note)
$txt =~ s/[^a-zA-Z\d\s]//g;  # drop punctuation
my @data = split(/ +/, $txt);
```

Consequences:

| Input | Becomes | Why it matters |
| --- | --- | --- |
| `Alice's` | `alices` | No possessive split; `alice` and `alices` are different terms |
| `don't` | `dont` | Apostrophes disappear |
| `them—and` or `them,and` | `themand` | Em-dashes and commas leave no space, so two words glue together |
| `White-Rabbit` | `whiterabbit` | Hyphens glue |
| `CHAPTER I.` | `chapter` + `i` | Roman numerals and headings stay in the bag |
| `[Alice's Adventures … 1865]` | `1865` as a term | File headers are not stripped |

The `tr/[A-Z]/[a-z]/` range also includes the literal brackets `[` and `]` in both sides of the transliteration. Those characters are deleted by the next substitution anyway, so the extra mappings are harmless here.

There is **no stemmer** and **no stopword list**. idf is the only thing that demotes `the`. That is pedagogically clean and linguistically crude.

## Empty tokens still increment the tf denominator

```perl
foreach my $d (@data)
{
    $word_count++;          # always
    if($d ne "")
    {
        $tf{$d}++;
        $df{$d}{$f}=1;
    }
}
```

`split(/ +/, …)` can yield empty fields (leading space, or punctuation-only lines that collapse to nothing). Those empties inflate `word_count` and therefore **shrink every tf in that document**. The four-file toy corpus in `examples/` is written without leading/trailing blank tokens so the hand calculation matches the runner.

The Python helper `examples/tfidf_mini.py` exposes both behaviors:

- `faithful=True` — same empty-token denominator as Perl
- `faithful=False` — denominator is the number of non-empty tokens

## `$#files` is not “number of documents”

```perl
opendir(DIR,"gutenberg");
my @files = readdir(DIR);
# ...
my $n = $#files;
my $idf_val = log($n/($#vals+1));
```

`readdir` normally returns `.`, `..`, and every filename. `$#files` is the last index, not the count of processed texts.

The committed `output/idf.txt` has a ceiling of `2.89037175789616 = ln(18)`, which matches **18 documents**. If you rerun the script in an environment where `@files` has a different length (dot entries, a stray `.DS_Store`, an extra text), every idf shifts.

The example runner uses the count of files it actually parsed:

```text
N = number of documents read
idf(t) = ln(N / df(t))
```

That is the definition the prose in these docs uses. If you need bit-identical output with a particular historical run, pin \(N\) and the file list.

Changing \(N\) does not add a constant to every tf-idf row. The extra term is \(\mathrm{tf}(t)\cdot\Delta\ln N\), which is larger for high-tf words, so **rankings can change**.

## df is stored as a set of filenames

`$df{$d}{$f}=1` then `keys %{ $df{$t} }`. A word that appears 400 times in *Moby-Dick* and once in *Emma* has `df = 2`. That is correct for idf and surprising if you expected a collection-wide term count.

`output/df.txt` prints those filenames in hash order. Do not treat the order as ranked.

## The product script depends on `Text::CSV_XS`

`tf*idf-product.pl` parses TSV through `Text::CSV_XS`. This environment does not ship that module by default. The files themselves are simple `term<TAB>number` lines; `examples/top_terms.py` and `examples/top_terms.pl` do not need the CPAN module.

If a line fails to parse, the product script prints `Error: …` and continues. It does not write a partial row for that term.

## Alphabetical output vs numeric ranking

`tf-idf-values.pl` and `tf*idf-product.pl` iterate `sort keys %hash`. That is **lexicographic by term**, so `alice` sits near the top of Alice’s file by accident (it starts with `a`) and `whale` sits far down in Moby-Dick.

Unix `sort -k2 -n` does not parse `1.23e-05` the way you want on every platform. Use `sort -k2 -g` or the Python helper.

## Zeros print as `0`

Perl stringifies a numeric zero as `0`, not `0.0000`. A row that looks like an integer is still a score. Do not filter “non-floats.”

## In-memory slurp

Each Gutenberg file is read with `my @text = <IN>`. Fine for this pocket corpus; the KJV is the stress case (~100k lines). There is no encoding layer: the files are plain ASCII-ish Gutenberg dumps. Fancy apostrophes and em-dashes, when present, become glue or disappear.

## `tf*idf-product.pl` does not close the output handle in a loop-friendly way

It opens `output/tfidf/$f` inside the file loop and writes, then moves on. Perl will close the handle on the next `open` or at process end. Harmless here; noted so a rewrite can `close(OUT)` explicitly (the tf writer already does).

## Precomputed `output/` is a snapshot

The numbers quoted in [interpreting-results.md](interpreting-results.md) are from the committed tables, not from a fresh run in this workspace. If you change tokenization or \(N\) and regenerate, update those quotes or compare against `examples/sample-sessions/` after regenerating those too.
