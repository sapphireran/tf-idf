#!/usr/bin/env perl
use strict;
use warnings;
use File::Basename qw(basename);

# Tiny teaching clone of the 2012 Perl pipeline.
#
# Differences from the scripts in the repository root:
#   * N is the number of tokenized documents, not $#files from readdir
#   * TSV is split on tabs instead of pulling in Text::CSV_XS
#   * rankings are printed to stdout instead of only writing files
#
# Usage (from the repository root):
#   perl examples/tiny_tfidf.pl examples/tiny-corpus
#   perl examples/tiny_tfidf.pl examples/classic-three-docs

my $corpus = $ARGV[0] // "examples/tiny-corpus";
opendir(my $dh, $corpus) or die "cannot open $corpus: $!";
my @names = grep { $_ !~ /^\./ && $_ =~ /\.txt$/ } readdir($dh);
closedir($dh);
@names = sort @names;
die "no .txt files in $corpus\n" unless @names;

my %tf_tables;
my %df;
foreach my $name (@names) {
    open(my $in, "<:encoding(UTF-8)", "$corpus/$name") or die $!;
    local $/;
    my $text = <$in>;
    close($in);

    $text =~ s/[\h\v]+/ /g;
    $text =~ tr/A-Z/a-z/;
    $text =~ s/[^a-z0-9\s]//g;
    my @tokens = grep { $_ ne "" } split(/ +/, $text);
    my $word_count = scalar @tokens;
    next if $word_count == 0;

    my %tf;
    foreach my $token (@tokens) {
        $tf{$token}++;
        $df{$token}{$name} = 1;
    }
    foreach my $term (keys %tf) {
        $tf{$term} = $tf{$term} / $word_count;
    }
    $tf_tables{$name} = \%tf;
}

my $n = scalar keys %tf_tables;
die "no non-empty documents\n" unless $n;

foreach my $name (sort keys %tf_tables) {
    print "=== $name ===\n";
    my %tfidf;
    my $tf = $tf_tables{$name};
    foreach my $term (keys %$tf) {
        my $df_term = scalar keys %{ $df{$term} };
        my $idf = log($n / $df_term);
        $tfidf{$term} = $tf->{$term} * $idf;
    }
    my @ranked = sort { $tfidf{$b} <=> $tfidf{$a} || $a cmp $b } keys %tfidf;
    my $limit = @ranked < 8 ? $#ranked : 7;
    foreach my $i (0 .. $limit) {
        my $term = $ranked[$i];
        printf "  %-12s  %.6f\n", $term, $tfidf{$term};
    }
    print "\n";
}

print "N=$n documents, vocabulary=" . (scalar keys %df) . " terms\n";
