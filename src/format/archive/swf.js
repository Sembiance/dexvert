import {Format} from "../../Format.js";

export class swf extends Format
{
	name           = "Shockwave/Macromedia Flash";
	website        = "http://fileformats.archiveteam.org/wiki/SWF";
	ext            = [".swf"];
	forbidExtMatch = true;
	magic          = [
		"Macromedia Flash data", "Macromedia Flash Player Movie", "Macromedia Flash Datei", "Macromedia Flash Player Compressed Movie", "Format: Small Web Format", "Uncompressed Adobe Flash SWF", "application/vnd.adobe.flash.movie",
		"SWF (ShockWave Flash) (swf)",
		/^SWF$/, /^fmt\/(104|105|106|107|108|109|110|505|506|507|757|758|759|760|761|762|763|766)( |$)/];
	idMeta     = ({macFileType, macFileCreator}) => (macFileType==="SWFL" && ["SWF2", "TVOD"].includes(macFileCreator)) ||
		(macFileType==="MMCH" && macFileCreator==="MSIE");
	converters = ["ffdec", "swfextract", "ffmpeg"];
}
