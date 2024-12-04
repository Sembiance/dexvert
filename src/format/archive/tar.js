import {Format} from "../../Format.js";

export class tar extends Format
{
	name           = "Tape Archive";
	website        = "http://fileformats.archiveteam.org/wiki/Tape_Archive";
	ext            = [".tar", ".gtar"];
	magic          = [
		// generic
		"TAR - Tape ARchive", "LZMA compressed Tape ARchive", "TAR Archiv gefunden", "Archive: tar", "application/x-tar", /.* tar archive/, /^tar archive/, /^Tar$/, /^x-fmt\/265( |$)/,

		// specific
		"Ruby Gem package", "Open Virtualization Format package", "Open Virtualization Format Archive", "Sony Ericsson Theme (for mobile phones)"
	];
	weakMagic      = [/^Tar$/];
	idMeta         = ({macFileType}) => macFileType==="TARF";
	forbiddenMagic = ["TFMX module sound data tar archive"];
	converters     = ["tar", "sevenZip", "deark[module:tar]", "unar[strongMatch]", "sqc", "izArc[matchType:magic]", "UniExtract[matchType:magic][hasExtMatch]"];
}
