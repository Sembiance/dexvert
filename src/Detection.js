import {xu, fg} from "xu";
import {validateClass} from "validator";
import {DexFile} from "./DexFile.js";
import {Program} from "./Program.js";

export const DETECTOR_PROGRAMS = ["file", "trid", "checkBytes", "dexmagic", "perlTextCheck", "ancientID", "amigaBitmapFontContentDetector"];

export const TEXT_MAGIC_STRONG =
[
	// checkBytes
	"Printable ASCII",

	// file
	"ASCII text", "ISO-8859 text", "UTF-8 Unicode text", "Non-ISO extended-ASCII text", "ReStructuredText file", "International EBCDIC text", "UTF-8 Unicode text", "Unicode text, UTF-8 text",
	"Algol 68 source, ISO-8859 text",	// Algol 68 is often mis-identified, usually confused with Pascal files. Just treat it as regular text
	
	// trid
	"Text - UTF-8 encoded"
];

export const TEXT_MAGIC_WEAK =
[
	// perlTextCheck
	"Likely Text (Perl)"
];

export const TEXT_MAGIC = [...TEXT_MAGIC_STRONG, ...TEXT_MAGIC_WEAK];


/* eslint-disable prefer-named-capture-group */
// These magics are VERY untrustworthy and any detections against them should be noted as such
const WEAK_VALUES =
[
	// dexmagic: WEAK checks
	/^IFF CAT file$/,
	
	// FILE: Very weak checks:
	/^0421 Alliant compact executable/,
	/^370 sysV/,
	/^370 XA sysV/,
	/^0420 Alliant virtual executable/,
	/^5View capture file/,
	/^64-bit XCOFF executable or object module/,
	/^AIX core file/,
	/^ALAN game data/,
	/^Alpha compressed COFF$/,
	/^Alpha u-code object$/,
	/^AmigaOS bitmap font/,
	/^Apache Avro/,
	/^Apache Hadoop Sequence/,
	/^Apache Hive RC file/,
	/^Apache ORC/,
	/^Apache Parquet/,
	/^Apple DiskCopy 4.2 image/,
	/^assembler source/,
	/^b\.out/,
	/^basic-16 executable/,
	/^BS image/,
	/^Clarion Developer/,
	/^Common Data Format \(Version 2\.5 or earlier\) data$/,
	/^Compiled PSI/,
	/^ddis\/ddif/,
	/^diff output/,
	/^dBase I[IV]I? DBT/,
	/^disk quotas file/,
	/^DIY-Thermocam raw data/,
	/^Dyalog APL/,
	/ECOFF executable/,
	/^Encore unsupported executable/,
	/^fsav macro virus signatures/,
	/^gfxboot compiled html help/,
	/^Generic INItialization configuration/,
	/^GEM NOSIG/,
	/^GeoSwath RDF$/,
	/^GTA audio index data/,
	/^GTA script/,
	/^Hitachi SH/,
	/^HTML document/,
	/^hp300/,
	/^iAPX 286 executable/,
	/^(little|big) endian ispell/,
	/^Java.*KeyStore$/,
	/^locale data table/,
	/^lif file/,
	/^MacBinary II,/,
	/^Maple help database$/,
	/^Matlab v4/,
	/^mc68k COFF object/,
	/^mc68k executable/,
	/^Microsoft a\.out/,
	/^MIPSEB Ucode/,
	/^MMDF mailbox$/,
	/^Motorola S-Record; binary data in text format$/,
	/^MPEG-4 LOAS/,
	/^MSXiE archive data/,
	/^Novell LANalyzer capture file$/,
	/^Perkin-Elmer executable/,
	/^PEX Binary Archive$/,
	/^Par archive data$/,
	/^Picasso 64 Image$/,
	/^OpenPGP Public Key/,
	/^OpenPGP Secret Key/,
	/^PGP encrypted data/,
	/^PGP key security ring/,
	/^PGP Secret Sub-key/,
	/^PGP symmetric key encrypted data/,
	/^PDP-11/,
	/^RAGE Package Format/,
	/^raw G3/,
	/^RDI Acoustic Doppler Current Profiler/,
	/^Sega FILM\/CPK Multimedia/,
	/spot sensor temperature/,
	/^SysEx File/,
	/^StarOffice Gallery theme/,
	/^SVR2 pure executable/,
	/^SVr\d curses screen image/,
	/^TeX font metric data/,
	/^troff or preprocessor input/,
	/^Targa image data/,
	/^unknown demand paged pure executable/,
	/^unknown readable demand paged pure executable/,
	/^VAX-order/,
	/^VISX image file/,
	/^Windows boot log/,
	/^Windows Precompiled iNF/,
	/^Windows SYSTEM.INI/,
	/^Windows WIN.INI/,
	/^X1 archive data/,
	/^X11 SNF font data/,
	/^Zebra Metafile graphic/,

	// TRID: Checks just 1-3 bytes:
	/^1ST Word Plus Document$/,
	/^5View capture$/,
	/^Affix file$/,
	/^Agfa\/Matrix SCODL bitmap$/,
	/^Amiga bitmap Font/,
	/^Any Password data$/,
	/^Atari XE Executable$/,
	/^ARHANGEL compressed archive$/,
	/^BALZ compressed data$/,
	/^Bennet Yee's face format bitmap$/,
	/^Bio-Rad Image\(s\) bitmap$/,
	/^Binary NX Vibration data/,
	/^BSArc compressed archive$/,
	/^C64 Hires bitmap$/,
	/^Cardwar Cards deck$/,
	/^Commodore .+ BASIC .+ program$/,
	/^Compact compressed data/,
	/^Continuous Wave Accelerometry data$/,
	/^Corel Color Palette$/,
	/^CyberAIDS infected Apple 2 executable$/,
	/^Cybiko Picture bitmap$/,
	/^dBASE IV Multiple index$/,
	/^DEGAS low-res compressed bitmap$/,
	/^DEGAS med-res bitmap$/,
	/^DEGAS med-res compressed bitmap$/,
	/^DEGAS hi-res bitmap$/,
	/^DEGAS hi-res compressed bitmap$/,
	/^DICOM medical imaging bitmap/,
	/^Digital Micrograph Script$/,
	/^DiskDupe 5\.12 disk image$/,
	/^Drazpaint \(C64\) bitmap$/,
	/^FinePrint saved output$/,
	/^Flexible Line Interpretation bitmap$/,
	/^F\.R\.A\.C\. project$/,
	/^Freeze! compressed archive$/,
	/^Generic INI configuration$/,
	/^GIF bitmap \(generic\)$/,
	/^GNU Privacy Guard public keyring \(generic\)$/,
	/^GraphiCode Programmable Device Format$/,
	/^Interpaint bitmap$/,
	/^IPLAY Enterprise Video$/,
	/^ISIS sketch$/,
	/^JCALG1 compressed data$/,
	/^Jovian Logic VI bitmap$/,
	/^Jupiter Ace snapshot$/,
	/^Koala Paint/,
	/^Lepton bitmap/,
	/^LTAC compressed audio/,
	/^LTP Nuclear ZX tape image$/,
	/^Luxor ABC80 tokenized BASIC source$/,
	/^LZMA compressed archive$/,
	/^Maple Common Binary file \(generic\)$/,
	/^Melco embroidery design$/,
	/^Microsoft Help \(old\)$/,
	/^Mozart functor$/,
	/^MP3 audio/,
	/^MSX2 ROM Image$/,
	/^null bytes$/,
	/^Oberon V4 Symbol data$/,
	/^OMF - Relocatable Object Module Format$/,
	/^OS\/2 Bitmap Graphics Array \(generic\)$/,
	/^packPNM compressed /,
	/^PaintShow Font$/,
	/^PGN \(Portable Gaming Notation\) Compressed format$/,
	/^Philips Respironics M-Series data format$/,
	/^Pixel image$/,
	/^PrintFox\/Pagefox bitmap/,
	/^Python Pickle serialized data/,
	/^Qmage encoded data$/,
	/^raw Group 3 FAX bitmap$/,
	/^RPG Maker data$/,
	/^Scitex Continuous Tone bitmap$/,
	/^Spectrum 512 Anispec animation$/,
	/^Spectrum emulator snapshot$/,
	/^SpeedScript document \(C64\)$/,
	/^Text - UTF-16/,
	/^TextEngine document \(generic\)$/,
	/^That's Write document$/,
	/^TTComp archive/,
	/^VGAPaint 386 module$/,
	/^VisiCalc spreadsheet$/,
	/^WhatsApp encrypted database$/,
	/^WillDraw Drawing$/,
	/^WordPerfect document \(Amiga\)$/,
	/^X1 compressed archive$/,
	/^XBase DataBase \(generic\)$/,
	/^Z-Code V\d adventure for Infocom Z-Machine$/,
	
	// TRID: Checks for just zeroes or nearly all zeroes:
	/^Adobe PhotoShop Brush$/,
	/^AudioZip encoded audio$/,
	/^bCAD Drawing$/,
	/^CAJ database$/,
	/^Dr\. Halo Font$/,
	/^Dyalog APL transfer$/,
	/^HP Logical Interchange Format disk image$/,
	/^Install Maker( Pro)? project$/,
	/^Intel CPU Microcode$/,
	/^Inset PIX bitmap$/,
	/^Lotus 123\/Symphony worksheet\/format\/configuration \(V1-V2\)$/,
	/^MacBinary [12]$/,
	/^Microsoft Works for Mac document \(v1\.0\)$/,
	/^Memo File Apollo Database Engine$/,
	/^Music Craft Score$/,
	/^OS\/2 Dynamic Link Library \(no DOS stub\)$/,
	/^Palantir WinTime Plan$/,
	/^Pegasus SPS encoded audio$/,
	/^Photoshop Action$/,
	/^PlayStation Hierarchical 3D Model Data$/,
	/^PlayStation high-speed 3D modeling data$/,
	/^Sierra AGI music format$/,
	/^Sybase iAnywhere database files$/,
	/^Take Command: 2nd Manassas game data archive$/,
	/^UbiArt Framework Cooked Asset$/,
	/^V-Ray Material \(binary\)$/,
	/^VXD Driver$/,
	/^Windows Device Dependent Bitmap$/,
	/^Windows Jump List$/,
	/^Windows Icon/,

	// TRID: Weak in some other way, such as common prefix/global strings
	/^Amiga Disk image File \(generic\)$/,
	/^Dan Bricklin's Demo/,
	/^Novastorm Media audio$/,
	/^Scalable Vector Graphics \(var\.3\)$/,
	/^SMS Super File$/,
	/^Stunt Island Film$/
];
/* eslint-enable prefer-named-capture-group */

export class Detection
{
	// builder to get around the fact that constructors can't be async
	static create({value, from, file, confidence=100, extensions=[]})
	{
		const detection = new this();
		Object.assign(detection, {value, from, file, confidence, extensions});
		detection.weak = WEAK_VALUES.some(v => v.test(value)) || confidence<5;

		validateClass(detection, {
			// required
			value      : {type : "string", required : true},						// the value of the detection
			from       : {type : "string", required : true},						// which programid produced the value
			file       : {type : DexFile, required : true},							// the file that this detection is for
			confidence : {type : "number", required : true, range : [0, 100]},		// what confidence level this detection is. Default: 100
			extensions : {type : ["string"], required : true, allowEmpty : true}, 	// list of extensions that are expected with this type of detection. Default: []
			weak       : {type : "boolean", required : true}						// if set to true this is a weak detection and should not be trusted too highly
		});

		return detection;
	}

	pretty(prefix="")
	{
		return `${prefix}${fg.orange(this.from.padStart(8, " "))} ${fg.white(this.confidence.toString().padStart(3, " "))}% ${fg.magenta(this.value)}${this.weak ? fg.deepSkyblue("weak") : ""}`;
	}
}

export async function getDetections(f, {xlog}={})
{
	return (await Promise.all(DETECTOR_PROGRAMS.map(programid => Program.runProgram(programid, f, {xlog, autoUnlink : true})))).flatMap(o => o.meta.detections);
}
