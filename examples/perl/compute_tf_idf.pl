#!/usr/bin/env perl
# Cleaned tf-idf walkthrough in the same spirit as the 2012 scripts.
#
#   perl examples/perl/compute_tf_idf.pl \
#       --input examples/tiny-corpus \
#       --output examples/_scratch/tiny-perl
#
# Differences from tf-idf-values.pl / tf*idf-product.pl:
#   * --input and --output instead of hardcoded gutenberg/ and output/
#   * N is the number of files actually tokenized
#   * empty tokens do not inflate the tf denominator
#   * no Text::CSV_XS dependency (split on tab)
#   * one process writes tf, df, idf, and tfidf
use strict;
use warnings;
use File::Basename qw(basename);
use File::Path qw(make_path);
use Getopt::Long qw(GetOptions);

my $input_dir  = "gutenberg";
my $output_dir = "examples/_scratch/perl-out";
my $top        = 10;
GetOptions(
    "input=s"  => \$input_dir,
    "output=s" => \$output_dir,
    "top=i"    => \$top,
) or die "usage: $0 --input DIR --output DIR [--top N]\n";

opendir(my $dh, $input_dir) or die "cannot read $input_dir: $!";
my @names = grep { !/^\./ && -f "$input_dir/$_" && /\.txt$/ } readdir($dh);
closedir($dh);
@names = sort @names;
die "no .txt files in $input_dir\n" unless @names;

my %df;
my %docs;
for my $name (@names) {
    open(my $in, "<", "$input_dir/$name") or die "cannot read $input_dir/$name: $!";
    my %tf_count;
    my $word_count = 0;
    while (my $txt = <$in>) {
        chomp $txt;
        $txt =~ s/[\h\v]+/ /g;
        $txt =~ tr/[A-Z]/[a-z]/;
        $txt =~ s/[^a-zA-Z\d\s]//g;
        for my $token (split / +/, $txt) {
            next if $token eq "";
            $word_count++;
            $tf_count{$token}++;
            $df{$token}{$name} = 1;
        }
    }
    close $in;
    $docs{$name} = { counts => \%tf_count, length => $word_count };
}

my $n = scalar @names;
my $tf_dir    = "$output_dir/tf";
my $tfidf_dir = "$output_dir/tfidf";
make_path($tf_dir, $tfidf_dir);

open(my $df_out, ">", "$output_dir/df.txt") or die $!;
open(my $idf_out, ">", "$output_dir/idf.txt") or die $!;
print {$df_out} "word\t#docs it exists in\tdoc names\n";

my %idf;
for my $term (sort keys %df) {
    my @files = sort keys %{ $df{$term} };
    my $document_freq = scalar @files;
    my $idf_val = log($n / $document_freq);
    $idf{$term} = $idf_val;
    print {$df_out} $term, "\t", $document_freq, "\t", join(", ", @files), "\n";
    print {$idf_out} $term, "\t", $idf_val, "\n";
}
close $df_out;
close $idf_out;

print "N=$n  documents=", scalar(@names), "\n\n";
for my $name (@names) {
    my $counts = $docs{$name}{counts};
    my $length = $docs{$name}{length} || 1;
    my %tfidf;
    open(my $tf_out, ">", "$tf_dir/$name") or die $!;
    open(my $tfidf_out, ">", "$tfidf_dir/$name") or die $!;
    for my $term (sort keys %$counts) {
        my $tf = $counts->{$term} / $length;
        my $score = $tf * $idf{$term};
        $tfidf{$term} = $score;
        print {$tf_out} $term, "\t", $tf, "\n";
        print {$tfidf_out} $term, "\t", $score, "\n";
    }
    close $tf_out;
    close $tfidf_out;

    print "## $name\n\n";
    print "| rank | term | tf-idf |\n| ---: | --- | ---: |\n";
    my $rank = 0;
    for my $term (sort { $tfidf{$b} <=> $tfidf{$a} || $a cmp $b } keys %tfidf) {
        $rank++;
        last if $rank > $top;
        print "| $rank | $term | $tfidf{$term} |\n";
    }
    print "\n";
}

print STDERR "wrote tables under $output_dir\n";
