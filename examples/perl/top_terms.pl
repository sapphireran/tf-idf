#!/usr/bin/env perl
# Rank a two-column term<TAB>score TSV (the output/tfidf files).
# Stdlib only — no Text::CSV_XS — so it can be used without CPAN.
#
#   perl examples/perl/top_terms.pl output/tfidf/carroll-alice.txt 10

use strict;
use warnings;

my $path  = shift @ARGV or die "usage: $0 FILE [TOP]\n";
my $limit = defined $ARGV[0] ? $ARGV[0] : 10;

open my $in, "<", $path or die "cannot read $path: $!";
my %score;
while (my $line = <$in>) {
    chomp $line;
    next if $line eq "";
    my ($term, $value) = split /\t/, $line, 2;
    next unless defined $value;
    $score{$term} = $value + 0;
}
close $in;

my @ranked = sort { $score{$b} <=> $score{$a} || $a cmp $b } keys %score;
if ($limit < @ranked) {
    @ranked = @ranked[0 .. $limit - 1];
}

print "== $path\n";
foreach my $term (@ranked) {
    printf "  %-20s  %.8f\n", $term, $score{$term};
}
