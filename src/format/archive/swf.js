import {Format} from "../../Format.js";

export class swf extends Format
{
	name           = "Macromedia Flash";
	website        = "http://fileformats.archiveteam.org/wiki/SWF";
	ext            = [".swf"];
	forbidExtMatch = true;
	magic          = ["Macromedia Flash data", "Macromedia Flash Player Movie", "Macromedia Flash Datei", "Macromedia Flash Player Compressed Movie", /^SWF$/, /^fmt\/(104|107|108|109|110|505|506|507)( |$)/];
	converters     = ["ffdec", "swfextract", "ffmpeg"];
}
