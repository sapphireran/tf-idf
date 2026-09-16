#!/usr/bin/env perl
# Rank a term<TAB>score table without Text::CSV_XS.
#
# Usage:
#   perl examples/top_terms.pl output/tfidf/carroll-alice.txt
#   perl examples/top_terms.pl output/tfidf/shakespeare-macbeth.txt 20

use strict;
use warnings;

my $path = shift @ARGV;
my $limit = shift @ARGV;
$limit = 15 if !defined $limit || $limit eq "";

if (!defined $path || $path eq "-h" || $path eq "--help") {
    print STDERR "usage: perl examples/top_terms.pl TABLE [N]\n";
    exit($path ? 0 : 2);
}

open(my $in, "<", $path) or die "cannot read $path: $!";
my @rows;
while (my $line = <$in>) {
    chomp $line;
    next if $line eq "" || $line =~ /^word \t/;
    my ($term, $score) = split(/\t/, $line, 3);
    next if !defined $term || !defined $score;
    push @rows, [$term, $score + 0];
}
close($in);

@rows = sort { $b->[1] <=> $a->[1] || $a->[0] cmp $b->[0] } @rows;
if ($limit >= 0 && @rows > $limit) {
    @rows = @rows[0 .. $limit - 1];
}

print "# $path  (" . scalar(@rows) . " shown)\n";
printf "%4s  %-20s  %s\n", "rank", "term", "score";
my $rank = 1;
for my $row (@rows) {
    printf "%4d  %-20s  %.12g\n", $rank, $row->[0], $row->[1];
    $rank++;
}
