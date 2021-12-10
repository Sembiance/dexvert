import {Format} from "../../Format.js";

export class swf extends Format
{
	name           = "Macromedia Flash";
	website        = "http://fileformats.archiveteam.org/wiki/SWF";
	ext            = [".swf"];
	forbidExtMatch = true;
	magic          = ["Macromedia Flash data", "Macromedia Flash Player Movie"];
	converters     = ["ffdec", "swfextract", "ffmpeg"];
}
