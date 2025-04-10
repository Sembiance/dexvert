import {Format} from "../../Format.js";

export class vivo extends Format
{
	name         = "VivoActive Streaming Video";
	website      = "https://wiki.multimedia.cx/index.php/Vivo";
	ext          = [".viv"];
	magic        = ["Vivo streaming video", "Vivo video data", "Vivo (vivo)", /^fmt\/499( |$)/];
	idMeta       = ({macFileType, macFileCreator}) => macFileType==="vivo" && macFileCreator==="Vivo";
	metaProvider = ["mplayer"];
	converters   = ["nihav", "ffmpeg[format:vivo]"];
}
