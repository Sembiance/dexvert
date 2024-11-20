import {Format} from "../../Format.js";

export class frameMaker extends Format
{
	name           = "FrameMaker";
	website        = "http://fileformats.archiveteam.org/wiki/FrameMaker";
	ext            = [".fm", ".frm", ".doc"];
	forbidExtMatch = true;
	magic          = ["FrameMaker document", "application/vnd.framemaker", /^fmt\/(190|533|534|535|537|538)( |$)/];
	weakMagic      = ["application/vnd.framemaker"];
	idMeta         = ({macFileType, macFileCreator}) => ["FASL", "FRst"].includes(macFileType) && macFileCreator==="Fram";
	converters     = ["frameMaker"];
}
