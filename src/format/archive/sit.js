import {Format} from "../../Format.js";

export class sit extends Format
{
	name       = "Stuffit Archive";
	website    = "http://fileformats.archiveteam.org/wiki/StuffIt";
	ext        = [".sit"];
	magic      = ["StuffIt compressed archive", "Macintosh StuffIt Archive", "application/x-stuffit", /^Archive: SIT$/, /^StuffIt( \d)?$/, /^StuffIt Archive/, /^fmt\/399|1459|1460( |$)/];
	weakMagic  = [/^StuffIt Archive/];
	idMeta     = ({macFileType}) => ["SIT!", "SIT5", "SITD"].includes(macFileType);
	converters = ["unar[mac]", "deark[module:stuffit][mac]", "macunpack", "maconv"];
}
