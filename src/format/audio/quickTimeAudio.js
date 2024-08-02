import {xu} from "xu";
import {Format} from "../../Format.js";
import {_MOV_MAGIC, _MOV_EXT} from "../video/mov.js";
import {RUNTIME} from "../../Program.js";

export class quickTimeAudio extends Format
{
	name             = "Apple QuickTime Audio";
	website          = "http://fileformats.archiveteam.org/wiki/QuickTime";
	ext              = _MOV_EXT;
	magic            = _MOV_MAGIC;
	idMeta           = ({macFileType}) => macFileType==="MooV";
	confidenceAdjust = () => -10;	// Reduce by 10 so that mov matches first
	metaProvider     = ["ffprobe"];
	notes			 = `HUGE room for improvement here. Several files don't convert like "Demo Music File" and "BOMBER_BGM"`;
	converters       = r =>
	{
		const validConverters = ["ffmpeg[outType:mp3]"];
		if(RUNTIME.asFormat!=="audio/quickTimeAudio")
		{
			if(r.f.input.size<(xu.MB*25))
			{
				RUNTIME.forbidProgram.delete("qt_flatt");
				validConverters.push("qt_flatt[chainAs:audio/quickTimeAudio]");
			}
			else
			{
				RUNTIME.forbidProgram.delete("qtflat");
				validConverters.push("qtflat[chainAs:audio/quickTimeAudio]");
			}
		}

		return validConverters;
	};
}
