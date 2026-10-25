import {xu} from "xu";
import {Format} from "../../Format.js";

export class eaTQI extends Format
{
	name           = "Electronic Arts TQI Video";
	website        = "https://wiki.multimedia.cx/index.php/Electronic_Arts_TQI";
	ext            = [".tgq", ".tgv", ".wve"];
	forbidExtMatch = [".wve"];
	magic          = ["Electronic Arts ASF video", "Need for Speed 2 Video", "Electronic Arts Multimedia (ea)", /^x-fmt\/137( |$)/];
	weakMagic      = ["Electronic Arts Multimedia (ea)"];
	metaProvider   = ["ffprobe"];
	converters     = ["ffmpeg[format:ea]"];
}
