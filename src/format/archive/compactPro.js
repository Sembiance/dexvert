import {Format} from "../../Format.js";

export class compactPro extends Format
{
	name           = "Mac Compact Pro Archive";
	website        = "http://fileformats.archiveteam.org/wiki/Compact_Pro";
	ext            = [".cpt", ".sea"];
	forbidExtMatch = [".sea"];
	magic          = ["Mac Compact Pro archive", "Compact Pro"];
	weakMagic      = ["Mac Compact Pro archive"];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="PACT" || (macFileType==="VDat" && macFileCreator==="Vrki");
	priority       = this.PRIORITY.LOW;
	converters     = ["unar[type:Compact Pro][mac]", "macunpack[strongMatch]"];
}
