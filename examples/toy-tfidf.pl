#!/usr/bin/env perl
use strict;
use warnings;
use File::Basename qw(basename dirname);
use File::Path qw(make_path);
use File::Spec;

# Self-contained TF / DF / IDF / TF-IDF runner for examples/toy-corpus.
# Tokenization matches tf-idf-values.pl. Collection size N is the number
# of processed documents (not $#readdir). Writes under examples/toy-output/
# so the Gutenberg snapshot in output/ is left alone.

my $usage = <<'EOF';
Usage: perl examples/toy-tfidf.pl [--corpus DIR] [--out DIR] [--top N]

  --corpus DIR   Input texts (default: examples/toy-corpus)
  --out DIR      Output tree   (default: examples/toy-output)
  --top N        Print this many ranked terms per document (default: 8)

Rebuilds DIR/{tf,tfidf,df.txt,idf.txt} from scratch.
EOF

my $corpus = 'examples/toy-corpus';
my $out_dir = 'examples/toy-output';
my $top_n = 8;

while (@ARGV) {
    my $arg = shift @ARGV;
    if ($arg eq '--help' || $arg eq '-h') {
        print $usage;
        exit 0;
    }
    elsif ($arg eq '--corpus') {
        $corpus = shift @ARGV or die "--corpus needs a directory\n";
    }
    elsif ($arg eq '--out') {
        $out_dir = shift @ARGV or die "--out needs a directory\n";
    }
    elsif ($arg eq '--top') {
        $top_n = shift @ARGV or die "--top needs an integer\n";
        die "--top must be a positive integer\n" unless $top_n =~ /^\d+$/ && $top_n > 0;
    }
    else {
        die "Unknown argument: $arg\n$usage";
    }
}

die "Corpus directory not found: $corpus\n" unless -d $corpus;

my $tf_dir = File::Spec->catdir($out_dir, 'tf');
my $tfidf_dir = File::Spec->catdir($out_dir, 'tfidf');
make_path($tf_dir, $tfidf_dir);

opendir(my $dh, $corpus) or die "Cannot read $corpus: $!\n";
my @files = sort grep { $_ !~ /^\./ && -f File::Spec->catfile($corpus, $_) } readdir($dh);
closedir($dh);
die "No input files in $corpus\n" unless @files;

my $n_docs = scalar @files;
my %df;
my %tf_tables;
my %word_counts;

foreach my $file (@files) {
    my $path = File::Spec->catfile($corpus, $file);
    open(my $in, '<', $path) or die "Cannot read $path: $!\n";
    my @lines = <$in>;
    close($in);

    my %tf;
    my $word_count = 0;
    foreach my $line (@lines) {
        foreach my $token (tokenize($line)) {
            $word_count++;
            next if $token eq '';
            $tf{$token}++;
            $df{$token}{$file} = 1;
        }
    }
    $tf_tables{$file} = \%tf;
    $word_counts{$file} = $word_count;

    open(my $out, '>', File::Spec->catfile($tf_dir, $file)) or die $!;
    foreach my $token (sort keys %tf) {
        printf $out "%s\t%s\n", $token, ($tf{$token} / $word_count);
    }
    close($out);
}

my %idf;
open(my $df_out, '>', File::Spec->catfile($out_dir, 'df.txt')) or die $!;
print $df_out "word \t #docs it exists in \t doc names\n";
open(my $idf_out, '>', File::Spec->catfile($out_dir, 'idf.txt')) or die $!;
foreach my $token (sort keys %df) {
    my @docs = sort keys %{ $df{$token} };
    my $df_count = scalar @docs;
    print $df_out $token, "\t", $df_count, "\t", join(', ', @docs), ", \n";
    my $idf_val = log($n_docs / $df_count);
    $idf{$token} = $idf_val;
    print $idf_out $token, "\t", $idf_val, "\n";
}
close($df_out);
close($idf_out);

print "Processed $n_docs documents from $corpus\n";
print "N (processed documents) = $n_docs\n";
print "Vocabulary size         = " . (scalar keys %df) . "\n\n";

foreach my $file (@files) {
    my %tfidf;
    my $tf = $tf_tables{$file};
    my $word_count = $word_counts{$file};
    foreach my $token (keys %$tf) {
        my $tf_val = $tf->{$token} / $word_count;
        $tfidf{$token} = $tf_val * ($idf{$token} // 0);
    }

    open(my $out, '>', File::Spec->catfile($tfidf_dir, $file)) or die $!;
    foreach my $token (sort keys %tfidf) {
        print $out $token, "\t", $tfidf{$token}, "\n";
    }
    close($out);

    print "=== $file  (tokens=$word_count, unique=" . (scalar keys %$tf) . ") ===\n";
    my $shown = 0;
    foreach my $token (sort { $tfidf{$b} <=> $tfidf{$a} || $a cmp $b } keys %tfidf) {
        last if $shown >= $top_n;
        printf "  %-16s  tf=%8.5f  idf=%8.5f  tfidf=%8.5f\n",
            $token,
            $tf->{$token} / $word_count,
            $idf{$token},
            $tfidf{$token};
        $shown++;
    }
    print "\n";
}

print "Wrote $tf_dir/\n";
print "Wrote $tfidf_dir/\n";
print "Wrote " . File::Spec->catfile($out_dir, 'df.txt') . "\n";
print "Wrote " . File::Spec->catfile($out_dir, 'idf.txt') . "\n";

sub tokenize {
    my ($text) = @_;
    chomp($text);
    $text =~ s/[\h\v]+/ /g;
    $text =~ tr/[A-Z]/[a-z]/;
    $text =~ s/[^a-zA-Z\d\s]//g;
    return split(/ +/, $text);
}
