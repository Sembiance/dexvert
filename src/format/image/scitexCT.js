import {Format} from "../../Format.js";

export class scitexCT extends Format
{
	name           = "Scitex Continuous Tone";
	website        = "http://fileformats.archiveteam.org/wiki/Scitex_CT";
	ext            = [".ct", ".sct"];
	forbidExtMatch = true;
	magic          = ["Scitex Continuous Tone bitmap", /^x-fmt\/146( |$)/];
	converters     = ["nconvert", "corelPhotoPaint[outType:tiff]", "corelDRAW[strongMatch]"];
}
