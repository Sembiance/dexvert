import {Format} from "../../Format.js";

export class frameMaker extends Format
{
	name           = "FrameMaker";
	website        = "http://fileformats.archiveteam.org/wiki/FrameMaker";
	ext            = [".fm", ".frm", "doc"];
	forbidExtMatch = true;
	magic          = ["FrameMaker document", /^fmt\/(190|533|534|535|538)( |$)/];
	converters     = ["frameMaker"];
}
