# tf*idf-product.pl
#
# Pass 2 of the personal Gutenberg tf-idf toy.
# Reads output/idf.txt and every file in output/tf/, writes
# output/tfidf/<filename> as term<TAB> (tf * idf).
#
# Requires Text::CSV_XS (tab-separated). To rank a committed table
# without that module:
#   python3 examples/top_terms.py output/tfidf/carroll-alice.txt
#
# Usage (from the repo root, after tf-idf-values.pl):
#   perl 'tf*idf-product.pl'
#
# Notes: docs/pipeline.md, docs/script-reference.md

use strict;
use Text::CSV_XS;
my $csv = Text::CSV_XS->new({sep_char => "\t"});



#read all the IDF values
my %idf;
open(IN,"output/idf.txt");
while(my $line = <IN>)
{
    if($csv->parse($line))
    {
        my @cols = $csv->fields();
        $idf{$cols[0]}=$cols[1];
    }
}
close(IN);

opendir(DIR,"output/tf");
my @files = readdir(DIR);
foreach my $f (@files)
{
    if($f !~ /^\./)
    {
        print "Processing file: ".$f."\n";
        my %tfidf;
        open(IN,"output/tf/$f");
        while(my $line = <IN>)
        {
            if($csv->parse($line))
            {
                my @cols = $csv->fields();
                my $val = $cols[1] * $idf{$cols[0]};
                $tfidf{$cols[0]} = $val;
                
            }
            else
            {
                my $error = $csv->error_input;
                print "Error: ".$error."\n";
            }
        }
        close(IN);

        open(OUT,">output/tfidf/$f");
        foreach my $ti (sort keys %tfidf)
        {
            print OUT $ti."\t".$tfidf{$ti}."\n";
        }
    }
}