#!/usr/bin/env perl
use strict;
use warnings;
use File::Basename qw(basename);
use File::Spec;

# Rank a TF-IDF table (or a directory of them) without Text::CSV_XS.

my $usage = <<'EOF';
Usage: perl examples/top-terms.pl [--n N] [--dir DIR] [FILE ...]

  --n N      How many terms to print (default: 15)
  --dir DIR  Rank every non-dot file in DIR (default: output/tfidf
             when no FILE arguments are given)

Each FILE is a token<TAB>score table, such as output/tfidf/carroll-alice.txt
or examples/toy-output/tfidf/cats.txt.
EOF

my $n = 15;
my $dir;
my @files;

while (@ARGV) {
    my $arg = shift @ARGV;
    if ($arg eq '--help' || $arg eq '-h') {
        print $usage;
        exit 0;
    }
    elsif ($arg eq '--n') {
        $n = shift @ARGV or die "--n needs an integer\n";
        die "--n must be a positive integer\n" unless $n =~ /^\d+$/ && $n > 0;
    }
    elsif ($arg eq '--dir') {
        $dir = shift @ARGV or die "--dir needs a directory\n";
    }
    elsif ($arg =~ /^-/) {
        die "Unknown argument: $arg\n$usage";
    }
    else {
        push @files, $arg;
    }
}

if (!@files) {
    $dir = 'output/tfidf' unless defined $dir;
    die "Directory not found: $dir\n" unless -d $dir;
    opendir(my $dh, $dir) or die "Cannot read $dir: $!\n";
    @files = map { File::Spec->catfile($dir, $_) }
        sort grep { $_ !~ /^\./ && -f File::Spec->catfile($dir, $_) } readdir($dh);
    closedir($dh);
}

die "No TF-IDF tables to rank\n" unless @files;

foreach my $file (@files) {
    die "Not a file: $file\n" unless -f $file;
    my @rows;
    open(my $in, '<', $file) or die "Cannot read $file: $!\n";
    while (my $line = <$in>) {
        chomp $line;
        next if $line eq '';
        my ($token, $score) = split(/\t/, $line, 2);
        next unless defined $token && defined $score && $score =~ /^[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?$/;
        push @rows, [ $token, $score + 0 ];
    }
    close($in);

    @rows = sort { $b->[1] <=> $a->[1] || $a->[0] cmp $b->[0] } @rows;
    print "=== ", basename($file), " ===\n";
    my $limit = @rows < $n ? scalar @rows : $n;
    for my $i (0 .. $limit - 1) {
        printf "%2d  %-20s  %.8g\n", $i + 1, $rows[$i][0], $rows[$i][1];
    }
    print "\n";
}
