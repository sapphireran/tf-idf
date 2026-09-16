#!/usr/bin/env perl
use strict;
use warnings;
use File::Basename qw(basename);
use File::Spec;

# Look up DF, IDF, and per-document TF-IDF for one or more tokens.

my $usage = <<'EOF';
Usage: perl examples/lookup-term.pl [options] TERM [TERM ...]

  --df FILE        DF table   (default: output/df.txt)
  --idf FILE       IDF table  (default: output/idf.txt)
  --tfidf-dir DIR  TF-IDF dir (default: output/tfidf)

Terms are matched after the same lowercase / punctuation strip used
by the pipeline. Example:

  perl examples/lookup-term.pl alice whale emma the ham hamlet
EOF

my $df_file = 'output/df.txt';
my $idf_file = 'output/idf.txt';
my $tfidf_dir = 'output/tfidf';
my @terms;

while (@ARGV) {
    my $arg = shift @ARGV;
    if ($arg eq '--help' || $arg eq '-h') {
        print $usage;
        exit 0;
    }
    elsif ($arg eq '--df') {
        $df_file = shift @ARGV or die "--df needs a file\n";
    }
    elsif ($arg eq '--idf') {
        $idf_file = shift @ARGV or die "--idf needs a file\n";
    }
    elsif ($arg eq '--tfidf-dir') {
        $tfidf_dir = shift @ARGV or die "--tfidf-dir needs a directory\n";
    }
    elsif ($arg =~ /^-/) {
        die "Unknown argument: $arg\n$usage";
    }
    else {
        push @terms, $arg;
    }
}

die "Pass at least one TERM\n$usage" unless @terms;
@terms = map { normalize_term($_) } @terms;

my %idf = load_pair_table($idf_file);
my %df = load_df_table($df_file);

foreach my $term (@terms) {
    print "==== $term ====\n";
    if (exists $idf{$term}) {
        printf "idf\t%s\n", $idf{$term};
    }
    else {
        print "idf\t(not in idf table)\n";
    }
    if (exists $df{$term}) {
        printf "df\t%s\t%s\n", $df{$term}{count}, $df{$term}{docs};
    }
    else {
        print "df\t(not in df table)\n";
    }

    if (-d $tfidf_dir) {
        opendir(my $dh, $tfidf_dir) or die "Cannot read $tfidf_dir: $!\n";
        my @files = sort grep { $_ !~ /^\./ && -f File::Spec->catfile($tfidf_dir, $_) } readdir($dh);
        closedir($dh);
        my @hits;
        foreach my $file (@files) {
            my $path = File::Spec->catfile($tfidf_dir, $file);
            my $score = find_score($path, $term);
            push @hits, [ $file, $score ] if defined $score;
        }
        if (@hits) {
            @hits = sort { $b->[1] <=> $a->[1] || $a->[0] cmp $b->[0] } @hits;
            print "tfidf by document (non-zero or present rows):\n";
            foreach my $hit (@hits) {
                printf "  %-28s  %s\n", $hit->[0], $hit->[1];
            }
        }
        else {
            print "tfidf\t(no rows in $tfidf_dir)\n";
        }
    }
    print "\n";
}

sub normalize_term {
    my ($text) = @_;
    $text =~ s/[\h\v]+/ /g;
    $text =~ tr/[A-Z]/[a-z]/;
    $text =~ s/[^a-zA-Z\d\s]//g;
    $text =~ s/^\s+|\s+$//g;
    return $text;
}

sub load_pair_table {
    my ($path) = @_;
    die "Missing table: $path\n" unless -f $path;
    my %map;
    open(my $in, '<', $path) or die "Cannot read $path: $!\n";
    while (my $line = <$in>) {
        chomp $line;
        next if $line eq '' || $line =~ /^word\s/;
        my ($token, $value) = split(/\t/, $line, 2);
        next unless defined $token && defined $value;
        $map{$token} = $value;
    }
    close($in);
    return %map;
}

sub load_df_table {
    my ($path) = @_;
    die "Missing table: $path\n" unless -f $path;
    my %map;
    open(my $in, '<', $path) or die "Cannot read $path: $!\n";
    while (my $line = <$in>) {
        chomp $line;
        next if $line eq '' || $line =~ /^word\s/;
        my ($token, $count, $docs) = split(/\t/, $line, 3);
        next unless defined $token && defined $count;
        $docs = '' unless defined $docs;
        $map{$token} = { count => $count, docs => $docs };
    }
    close($in);
    return %map;
}

sub find_score {
    my ($path, $term) = @_;
    open(my $in, '<', $path) or die "Cannot read $path: $!\n";
    while (my $line = <$in>) {
        chomp $line;
        my ($token, $score) = split(/\t/, $line, 2);
        if (defined $token && $token eq $term) {
            close($in);
            return $score;
        }
    }
    close($in);
    return undef;
}
