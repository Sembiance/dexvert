import {Format} from "../../Format.js";

export class msCompress extends Format
{
	name           = "MS Compress Archive";
	website        = "http://fileformats.archiveteam.org/wiki/MS-DOS_installation_compression";
	ext            = ["_", ".exe"];
	forbidExtMatch = true;	// Just too common and we have pretty good magic
	safeExt        = "_";	// Even self extracting archives need to end in an underscore in order to decompress
	magic          = ["MS Compress archive data", "Microsoft SZDD compressed", "Microsoft KWAJ compressed", "MS DOS Compression Format", "Microsoft Compress", "MSC Archiv gefunden", /^fmt\/(462|469)( |$)/];
	converters     = ["msexpand", "msexpand_win2k", "deark[module:mscompress]", "UniExtract"];
}
