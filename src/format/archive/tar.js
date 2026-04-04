import {Format} from "../../Format.js";

export class tar extends Format
{
	name           = "Tape Archive";
	website        = "http://fileformats.archiveteam.org/wiki/Tape_Archive";
	ext            = [".tar", ".gtar"];
	magic          = [
		// generic
		"TAR - Tape ARchive", "LZMA compressed Tape ARchive", "TAR Archiv gefunden", "Archive: tar", "application/x-tar", /.* tar archive/, /^tar archive/, /^Tar$/, "deark: tar", /^x-fmt\/265( |$)/,
		"TAR - Tape ARchive (longname)", "TAR - Tape ARchive (directory)",

		// specific
		"Ruby Gem package", "Open Virtualization Format package", "Open Virtualization Format Archive", "Sony Ericsson Theme (for mobile phones)", /^AVM FRITZ!Box firmware/, "QNX Package (ungzipped)", "Unity Package (ungzipped)"
	];
	weakMagic      = ["TAR - Tape ARchive (longname)", "TAR - Tape ARchive (directory)"];
	idMeta         = ({macFileType}) => ["tar□", "TARF"].includes(macFileType);
	forbiddenMagic = ["TFMX module sound data tar archive"];
	converters     = ["tar", "sevenZip[type:tar]", "deark[module:tar]", "unar[strongMatch]", "sqc", "izArc[matchType:magic]", "UniExtract[matchType:magic][hasExtMatch]"];
}
