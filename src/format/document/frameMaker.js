import {Format} from "../../Format.js";

export class frameMaker extends Format
{
	name           = "FrameMaker";
	website        = "http://fileformats.archiveteam.org/wiki/FrameMaker";
	ext            = [".fm", ".frm", ".doc"];
	forbidExtMatch = true;
	magic          = ["FrameMaker document", "application/vnd.framemaker", /^fmt\/(190|302|533|534|535|536|537|538|539)( |$)/];
	idMeta         = ({macFileType, macFileCreator}) => ["FASL", "FRst", "sASL"].includes(macFileType) && ["Fra5", "Fram"].includes(macFileCreator);
	converters     = ["frameMaker"];
}
