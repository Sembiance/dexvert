import {Format} from "../../Format.js";

export class tar extends Format
{
	name           = "Tape Archive";
	website        = "http://fileformats.archiveteam.org/wiki/Tape_Archive";
	ext            = [".tar", ".gtar"];
	magic          = ["TAR - Tape ARchive", "LZMA compressed Tape ARchive", "TAR Archiv gefunden", "Archive: tar", /.* tar archive/, /^tar archive/, /^Tar$/, /^x-fmt\/265( |$)/];
	idMeta         = ({macFileType}) => macFileType==="TARF";
	forbiddenMagic = ["TFMX module sound data tar archive"];
	converters     = ["tar", "sevenZip", "deark[module:tar]", "unar", "sqc", "izArc", "UniExtract"];
}
