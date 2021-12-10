import {Format} from "../../Format.js";

export class swfEXE extends Format
{
	name           = "Macromedia Flash Compiled EXE";
	website        = "http://fileformats.archiveteam.org/wiki/SWF";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["Macromedia Projector/Flash executable"];
	converters     = ["EXE2SWFExtractor"];
}
