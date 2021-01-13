"use strict";
/* eslint-disable prefer-named-capture-group */
const XU = require("@sembiance/xu"),
	path = require("path");

const C = {};

// A list of family types. Order is the secondary order they will be matched in the case of multiple 'types' of matches (magic, etc, filename) across multiple categories
// If you add any here, you also need to update retromission.com msdos.styl
C.FAMILIES = ["archive", "document", "audio", "music", "video", "image", "3d", "font", "other", "executable", "rom", "text"];

// A priority to use if a file matches multiple times within a single family
C.PRIORITY =
{
	TOP      : 0,
	HIGH     : 1,
	STANDARD : 2,
	LOW      : 3,
	VERYLOW  : 4,
	LOWEST   : 5
};

C.FORMAT_DIR_PATH = path.join(__dirname, "format");

C.UNOCONV_PORT = 27359;

C.DEXSERV_HOST = "localhost";
C.DEXSERV_PORT = 17735;
C.DEXSERV_OK_RESPONSE = "a-ok";

C.TENSORSERV_HOST = "localhost";
C.TENSORSERV_PORT = 17736;
C.TENSORSERV_OK_RESPONSE = "a-ok";

C.MATCH_MAX_GARBAGE_PROBABILITIES =
{
	magic    : 0.7,
	filename : 0.6,
	ext      : 0.6,
	fileSize : 0.01,
	fallback : 0.01
};

C.GARBAGE_DETECTED_DIR_PATH = path.join(__dirname, "../tensor/garbage/detected");

C.TEXT_MAGIC = ["ASCII text", "ISO-8859 text", "UTF-8 Unicode text", "Non-ISO extended-ASCII text", "ReStructuredText file", "International EBCDIC text", "UTF-8 Unicode text", "Printable ASCII"];
C.GENERIC_MAGIC = [/^data$/, /^very short file \(no magic\)$/, /^null bytes$/];

// These magics are VERY untrustworthy and nothing should EVER match on them (but still keep them for record sakes)
C.UNTRUSTWORTHY_MAGIC =
[
	// FILE: Very weak checks:
	/^Apple DiskCopy 4.2 image/,
	/^assembler source/,
	/^basic-16 executable/,
	/^Clarion Developer/,
	/^diff output/,
	/^dBase I[IV]I? DBT/,
	/^DIY-Thermocam raw data/,
	/^Dyalog APL/,
	/^Hitachi SH/,
	/^HTML document/,
	/^iAPX 286 executable/,
	/^(little|big) endian ispell/,
	/^Java.*KeyStore$/,
	/^MacBinary II,/,
	/^mc68k executable/,
	/^Motorola S-Record; binary data in text format$/,
	/^Novell LANalyzer capture file$/,
	/^Par archive data$/,
	/^Picasso 64 Image$/,
	/^PGP key security ring/,
	/^PGP Secret Sub-key/,
	/^PGP symmetric key encrypted data/,
	/^PDP-11/,
	/^RDI Acoustic Doppler Current Profiler/,
	/^SysEx File/,
	/^TeX font metric data/,
	/^troff or preprocessor input/,
	/^Targa image data/,
	/^Windows boot log/,
	/^Windows Precompiled iNF/,
	/^Zebra Metafile graphic/,

	// TRID: Checks just 1-3 bytes:
	/^Affix file$/,
	/^Agfa\/Matrix SCODL bitmap$/,
	/^Any Password data$/,
	/^Atari XE Executable$/,
	/^C64 Hires bitmap$/,
	/^Cardwar Cards deck$/,
	/^Commodore .+ BASIC .+ program$/,
	/^DEGAS low-res compressed bitmap$/,
	/^DEGAS med-res bitmap$/,
	/^DEGAS med-res compressed bitmap$/,
	/^DEGAS hi-res bitmap$/,
	/^DEGAS hi-res compressed bitmap$/,
	/^Digital Micrograph Script$/,
	/^Generic INI configuration$/,
	/^GIF bitmap \(generic\)$/,
	/^GNU Privacy Guard public keyring \(generic\)$/,
	/^GraphiCode Programmable Device Format$/,
	/^Interpaint bitmap$/,
	/^ISIS sketch$/,
	/^Jupiter Ace snapshot$/,
	/^Koala Paint/,
	/^Luxor ABC80 tokenized BASIC source$/,
	/^Maple Common Binary file \(generic\)$/,
	/^Microsoft Help \(old\)$/,
	/^MP3 audio/,
	/^MSX2 ROM Image$/,
	/^OMF - Relocatable Object Module Format$/,
	/^OS\/2 Bitmap Graphics Array \(generic\)$/,
	/^PGN \(Portable Gaming Notation\) Compressed format$/,
	/^Philips Respironics M-Series data format$/,
	/^PrintFox\/Pagefox bitmap \(var\. [BGP]\)$/,
	/^Python Pickle serialized data/,
	/^That's Write document$/,
	/^VGAPaint 386 module$/,
	/^WordPerfect document \(Amiga\)$/,
	/^XBase DataBase \(generic\)$/,
	/^Z-Code V\d adventure for Infocom Z-Machine$/,
	
	// TRID: Checks for just zeroes or nearly all zeroes:
	/^Adobe PhotoShop Brush$/,
	/^bCAD Drawing$/,
	/^Dyalog APL transfer$/,
	/^Install Maker( Pro)? project$/,
	/^Intel CPU Microcode$/,
	/^Inset PIX bitmap$/,
	/^Lotus 123\/Symphony worksheet\/format\/configuration \(V1-V2\)$/,
	/^MacBinary [12]$/,
	/^Memo File Apollo Database Engine$/,
	/^OS\/2 Dynamic Link Library \(no DOS stub\)$/,
	/^Palantir WinTime Plan$/,
	/^Pegasus SPS encoded audio$/,
	/^Sybase iAnywhere database files$/,
	/^VXD Driver$/,
	/^Windows Device Dependent Bitmap$/,
	/^Windows Jump List$/,

	// TRID: Weak in some other way, such as global strings
	/^Amiga Disk image File \(generic\)$/,
	/^Dan Bricklin's Demo/,
	/^Scalable Vector Graphics \(var\.3\)$/
];

module.exports = C;
