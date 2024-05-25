import {xu} from "xu";
import {Format} from "../../Format.js";

export class eaTQI extends Format
{
	name         = "Electronic Arts TQI Video";
	website      = "https://wiki.multimedia.cx/index.php/Electronic_Arts_TQI";
	ext          = [".tgq"];
	magic        = ["Electronic Arts ASF video", "Need for Speed 2 Video", /^x-fmt\/137( |$)/];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
