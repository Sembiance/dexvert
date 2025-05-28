import {Format} from "../../Format.js";

export class sit extends Format
{
	name       = "Stuffit Archive";
	website    = "http://fileformats.archiveteam.org/wiki/StuffIt";
	ext        = [".sit"];
	magic      = ["StuffIt compressed archive", "Macintosh StuffIt Archive", "application/x-stuffit", /^Archive: SIT$/, /^StuffIt( \d)?$/, /^StuffIt Archive/, /^fmt\/(399|1459|1460)( |$)/];
	idMeta     = ({macFileCreator, macFileType}) => ["SIT!", "SIT2", "SIT5", "SITD", "STin"].includes(macFileType) || (macFileType==="disk" && macFileCreator==="SITx") || (macFileType==="rohd" && macFileCreator==="ddsk");
	converters = ["unar[mac]", "deark[module:stuffit][mac]", "macunpack", "maconv"];
}
