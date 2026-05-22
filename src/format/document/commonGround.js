import {Format} from "../../Format.js";

export class commonGround extends Format
{
	name           = "Common Ground";
	website        = "http://fileformats.archiveteam.org/wiki/Common_Ground";
	ext            = [".dp"];
	forbidExtMatch = true;
	magic          = ["Common Ground Digital Paper document"];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="CGDC" && ["CGVM", "RcDs"].includes(macFileCreator);
	converters     = ["vibe2pdf"];	// vibe converter not complete, but good enough for now
}
