import {Format} from "../../Format.js";

export class msCompress extends Format
{
	name           = "MS Compress Archive";
	website        = "http://fileformats.archiveteam.org/wiki/MS-DOS_installation_compression";
	ext            = ["_", ".exe"];
	forbidExtMatch = true;	// Just too common and we have pretty good magic
	safeExt        = dexState => (dexState.f.input.ext.endsWith("_") ? dexState.f.input.ext : "_");	// Even self extracting archives need to end in an underscore in order to decompress
	magic          = [
		"MS Compress archive data", "Microsoft SZDD compressed", "Microsoft KWAJ compressed", "MS DOS Compression Format", "Microsoft Compress", "MSC Archiv gefunden", "Archive: KWAJ", "Archive: SZDD", "deark: mscompress (MS Installation Compression",
		"Microsoft SZ compressed", "Archive: SZ[by Microsoft]", /^idarc: MS Compress( |$)/, /^fmt\/(462|469)( |$)/, "image:Bm_Format"];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="MSCF" && macFileCreator==="MSSU";
	converters = ["deark[module:mscompress][missingLetter]", "msexpand", "msexpand_win2k", "UniExtract"];
}
