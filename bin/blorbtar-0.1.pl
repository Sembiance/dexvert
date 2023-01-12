#!/usr/bin/perl -w
use strict;

# blorbtar 0.1 - tarlike interface to Blorb files
# Copyright (c) 2000 Evin Robertson
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  See http://www.gnu.org/copyleft/gpl.html for the terms of the
#  GNU General Public License.  If you don't have internet access, write to
#  the Free Software Foundation, Inc., 59 Temple Place, Suite 330,
#  Boston, MA 02111, USA.
#
#  The author can be reached at nitfol@my-deja.com

#
# Blorb is a file format for storing resources for Interactive Fictions
# games.  The specification is available at http://www.eblong.com/zarf/blorb/
#
# The blorb specification recommends interpreters allow resources to be
# spread around a directory instead of packaged to make development easier.
# Blorbtar takes these files and generates a Blorb file without requiring you
# first to write a 'blurb' file.
#
# All input files are expected to be standalone equivalents of what's inside
# blorb files.
#
# TODO:
#   - allow text versions of chunks (especially RESOL and RELEASE)
#   - IDENT chunk autogeneration
#   - 'SONG' type support (this is a MOD file which lacks samples of its own)
#   - Perhaps make the extension option ('e') use extensions for type
#     detection when creating Blorb files.
#   - maybe support the append ('r') and diff ('d') commands
#   - perhaps an option to be tar-compatible in the double verbose listing for
#     tar wrapping programs
#


         # base filename => [ Usage, Chunk type ]
my %namelist = ( PIC     => [ "Pict", \&PicType ],
		 SND     => [ "Snd ", \&SndType ],
		 STORY   => [ "Exec", \&GamType ],
		 PALETTE => [ 0, "Plte" ],
		 RESOL   => [ 0, "Reso" ],
		 LOOPING => [ 0, "Loop" ],
		 RELEASE => [ 0, "RelN" ],
		 IDENT   => [ 0, "IFhd" ],
		 COPY    => [ 0, "(c) " ],
		 AUTH    => [ 0, "AUTH" ],
		 ANNO    => [ 0, "ANNO" ],
		 SAGL    => [ 0, "SAGL" ],
		 );

          # chunk type => common extension
my %extlist = ( "JPEG" => "jpg",
		"PNG " => "png",
		"FORM" => \&FORM_ext,
		"MOD " => "mod",
		"Glul" => "ulx",
		"TADG" => "gam",
		"MSRL" => "mag",
		"ZCOD" => \&ZCOD_ext,
		"HUGO" => "hex",
		"ALAN" => "acd",
		"SAAI" => "dat",
		);


sub ZCOD_ext
{
    read BLORB, $_, 1;
    seek BLORB, -1, 1;
    return "z" . ord($_);
}

sub FORM_ext
{
    read BLORB, $_, 4;
    seek BLORB, -4, 1;
    return "aiff" if $_ eq "AIFF";
    return $_;
}


sub PicType
{
    my $magic;
    seek CHUNK, 0, 0;
    read CHUNK, $magic, 10;
    if($magic =~ /^\xff\xd8....JFIF/) {
	return "JPEG";
    }
    if($magic =~ /^\x89PNG\x0d\x0a\x1a\x0a/) {
	return "PNG ";
    }
    die "Unknown picture type!\n";
}


sub SndType
{
    my $magic;
    seek CHUNK, 0, 0;
    read CHUNK, $magic, 12;
    if($magic =~ /^FORM....AIFF/) {
	return "AIFF";
    }
    seek CHUNK, 1080, 0;
    read CHUNK, $magic, 4;
    if($magic eq "M.K." || $magic eq "M!K!") {
	return "MOD ";
    }

    die "Unknown sound type!\n";
}


sub GamType
{
    my $magic;
    seek CHUNK, 0, 0;
    read CHUNK, $magic, 64;
    if($magic =~ /^Glul/) {
	return "Glul";
    }
    if($magic =~ /^TADS2 bin\x0a\x0d\x1a\x00\x76/s) {
	return "TADG";
    }
    if($magic =~ /^MaSc/) {
	return "MSRL";
    }
    if($magic =~ /^(\x01|\x02|\x03|\x04|\x05|\x06|\x07|\x08).................[0-9][0-9][0-9][0-9][0-9][0-9]/s) {
        return "ZCOD";
    }
    if($magic =~ /^...[0-9][0-9]-[0-9][0-9]-[0-9][0-9].....................................\x00\x00\x00\x00\x00\x00\x00\x00/s) {
	return "HUGO";
    }
    if($magic =~ /^\x02[\x00-\x09][\x00-\x09][\x00-\x09]....\x00\x00\x00[\x00-\x01]........\x00\x00\x00[\x00-\x01]/s) {
	return "ALAN";
    }
    if($magic =~ /^\s*[0-9]+\s+[0-9]+\s+[0-9]+\s+[0-9]+\s+[0-9]+\s+/) {
	return "SAAI";
    }
    die "Unknown game type!\n";
}


sub bin32_num
{
    return vec($_[0], 0, 32);
}


sub num_bin32
{
    my $number = '';
    vec($number, 0, 32) = $_[0];
    return $number;
}

my $option_verbose = 0;
my $option_extension = 0;

sub list_file
{
    my ($usage, $number, $type, $length, $name) = @_;
    if($option_verbose) {
	if($option_verbose >= 2) {
	    if($usage) {
		printf "$usage %4d", $number;
	    } else {
		print "         ";
	    }
	    printf "  $type  %10d  ", $length;
	}
	print "$name\n";
    }

}

sub archive
{
    my @files = @_;
    my @usagelist;
    my @chunklist;

    my $usagesize = 0;
    my $chunksize = 0;
    my $offset = 0;

    if(!@files) {
	die "Cowardly refusing to create an empty blorb file.\n";
    }

    foreach my $f (@files) {
	my @chunkinfo;
	open CHUNK, "<$f";
	seek CHUNK, 0, 2;
	my $length = tell CHUNK;
	if($f =~ /^(.*\/)?(.*?)([0-9]+)?(\..*)?$/) {
	    if($namelist{uc $2}) {
		my $name = uc $2;
		my $usage = $namelist{$name}->[0];
		my $type;
		my $number;
		my $is_IFF;
		if(ref $namelist{$name}->[1]) {
		    $type = $namelist{$name}->[1]->();
		} else {
		    $type = $namelist{$name}->[1];
		}
		if(defined $3) {
		    $number = int($3);
		} else {
		    $number = 0;
		}
		if($usage) {
		    push @usagelist, [ $usage, $number, $offset ];
		    $usagesize += 12;
		}

		if($type eq "AIFF") { 
		    $is_IFF = 1;
		    $type = "FORM";
		}

		list_file($usage, $number, $type, $length, $f);

		if($is_IFF) {
		    $length -= 8;
		}
		push @chunklist, [ $f, $type, $length, $is_IFF ];

		if($length % 2) {
		    $length++;
		}

		$chunksize += 8 + $length;
		$offset += 8 + $length;
	    } else {
		print "Unknown resource type name: $f\n";
	    }
	} else {
	    print "Unparseable filename: $f\n";
	}
	close CHUNK;
    }

    print BLORB "FORM", num_bin32(4 + 12 + $usagesize + $chunksize), "IFRS";
    print BLORB "RIdx", num_bin32(4 + $usagesize), num_bin32($#usagelist + 1);
    foreach my $f (@usagelist) {
	print BLORB $f->[0], num_bin32($f->[1]),
	            num_bin32(24 + $usagesize + $f->[2]);
    }
    foreach my $f (@chunklist) {
	my $buffer;
	# If it's not an IFF file, create a chunk header for it
	if(!($f->[3])) {
	    print BLORB $f->[1], num_bin32($f->[2]);
	}
	open CHUNK, "<$f->[0]";
	seek CHUNK, 0, 0;
	while(read CHUNK, $buffer, 16384) {
	    print BLORB $buffer;
	}
	if(($f->[2]) % 2) {
	    print BLORB "\x0";
	}
    }
}

sub load_blorb
{
    my %file_mask;
    foreach $_ (@_) {
	$file_mask{lc $_} = 1;
    }

    my %usagelist;
    my @chunklist;

    my $total_size;

    read BLORB, $_, 4;
    if($_ ne "FORM") { die "Not an IFF file\n"; }
    read BLORB, $_, 4;
    $total_size = bin32_num($_);
    read BLORB, $_, 4;
    if($_ ne "IFRS") { die "IFF type $_ instead of IFRS\n"; }
    $total_size -= 4;

    read BLORB, $_, 4;
    if($_ ne "RIdx") { die "First chunk $_ instead of RIdx\n"; }
    read BLORB, $_, 4;
    my $index_size = bin32_num($_);
    read BLORB, $_, 4;
    my $index_count = bin32_num($_);
    if($index_size != 4 + $index_count * 12) { die "Bad RIdx size\n"; }
    $total_size -= 12 + $index_size;
    if($total_size < 0) { die "RIdx broken"; }
    for my $i (1..$index_count) {
	my ($usage, $number, $start);
	read BLORB, $usage, 4;
	read BLORB, $_, 4; $number = bin32_num($_);
	read BLORB, $_, 4; $start  = bin32_num($_);
	$usagelist{$start} = [ $usage, $number ];
    }

    while($total_size > 0) {
	my ($type, $size, $name, $location, $ext);
	$location = tell BLORB;
	read BLORB, $type, 4;
	read BLORB, $_, 4; $size = bin32_num($_);
	if($option_extension && $extlist{$type}) {
	    if(ref $extlist{$type}) {
		$ext = "." . $extlist{$type}->();
	    } else {
		$ext = "." . $extlist{$type};
	    }
	} else {
	    $ext = "";
	}
	seek BLORB, $size, 1;
	$total_size -= 8 + $size;
	if((tell BLORB) % 2) {
	    seek BLORB, 1, 1;
	    $total_size--;
	}
	if($usagelist{$location}) {
	    foreach my $pname (keys %namelist) {
		if($namelist{$pname}->[0] eq $usagelist{$location}->[0]) {
		    $name = $pname . $usagelist{$location}->[1] . $ext;
		}
	    }
	} else {
	    foreach my $pname (keys %namelist) {
		if($namelist{$pname}->[1] eq $type) {
		    $name = $pname . $ext;
		}
	    }
	}

	if(!%file_mask || $file_mask{lc $name}) {
	    push @chunklist, [ $usagelist{$location}, $type, $size, $name, $location + 8 ];
	}
    }

    return @chunklist;
}


sub unarchive
{
    my @chunklist = load_blorb(@_);

    foreach my $c (@chunklist) {
	my ($name, $location, $length) = ($c->[3], $c->[4], $c->[2]);
	my $buffer;
	list_file($c->[0]->[0], $c->[0]->[1], $c->[1], $c->[2], $c->[3]);
	open CHUNK, ">$name";
	if($c->[1] eq "FORM") {
	    print CHUNK "FORM", num_bin32($length);
	}

	seek BLORB, $location, 0;
	read BLORB, $buffer, $length;
	print CHUNK $buffer;
	close CHUNK;
    }
}

sub listarchive
{
    my @chunklist = load_blorb(@_);

    foreach my $c (@chunklist) {
	list_file($c->[0]->[0], $c->[0]->[1], $c->[1], $c->[2], $c->[3]);
    }
}


my $command = "";
my $commandoptions = $ARGV[0];
shift @ARGV;

if(!defined $commandoptions || $commandoptions eq "--help") {
    die
"blorbtar 0.1 - gives a tarlike interface to blorb archives.
Usage:
  blorbtar.pl command blorbfile [files]

The following commands and options are available
  c        create a blorb file
  x        extract files from a blorb file
  t        list files in blorb file
  v        do this verbosely (repeating makes it doubly so)
  e        Append appropriate extensions to filenames
";
}

while($_ = chop $commandoptions) {
    if($_ eq "-") { }     # Ignore so they can do -x if they like
    elsif($_ eq "f") { }  # Backward compatibility with your fingers
    elsif($_ eq "c") { $command = "c"; }
    elsif($_ eq "x") { $command = "x"; }
    elsif($_ eq "t") { $command = "t"; }
    elsif($_ eq "v") { $option_verbose++; }
    elsif($_ eq "e") { $option_extension = 1; }
    else {  die "Unknown option or command: $_\n"; }    
}

my $blorbfile = $ARGV[0];
shift @ARGV;

if(!defined $blorbfile) {
    die "You must specify a Blorb file.\n";
}

if($command eq "c") {
    open BLORB, ">$blorbfile" || die "Cannot open \"$blorbfile\" for writing.\n";
    archive(@ARGV);
    close BLORB;
} elsif($command eq "x") {
    open BLORB, "<$blorbfile" || die "Cannot open \"$blorbfile\" for reading.\n";
    unarchive(@ARGV);
    close BLORB;
} elsif($command eq "t") {
    open BLORB, "<$blorbfile" || die "Cannot open \"$blorbfile\" for reading.\n";
    $option_verbose++;
    listarchive(@ARGV);
    close BLORB;
} else {
    die "You must give a command (one of c, x, or t).\n";
}
