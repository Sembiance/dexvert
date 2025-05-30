import {Format} from "../../Format.js";

export class sit extends Format
{
	name           = "Stuffit Archive";
	website        = "http://fileformats.archiveteam.org/wiki/StuffIt";
	ext            = [".sit", ".sea"];
	forbidExtMatch = [".sea"];
	magic          = [
		"StuffIt compressed archive", "Macintosh StuffIt Archive", "Mac StuffIt Self-Extracting Archive", "application/x-stuffit", /^Archive: SIT$/, /^StuffIt( \d)?$/, /^StuffIt Archive/, "deark: stuffit (StuffIt, old format)",
		/^fmt\/(399|1459|1460)( |$)/];
	idMeta     = ({macFileCreator, macFileType}) => ["SIT!", "SIT2", "SIT5", "SITD", "STin"].includes(macFileType) || (macFileType==="disk" && macFileCreator==="SITx") || (macFileType==="rohd" && macFileCreator==="ddsk");
	converters = ["unar[type:StuffIt][mac]", "deark[module:stuffit][mac]", "macunpack[strongMatch]", "maconv[strongMatch]"];
}
