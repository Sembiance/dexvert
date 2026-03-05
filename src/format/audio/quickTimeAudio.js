import {xu} from "xu";
import {Format} from "../../Format.js";
import {_MOV_MAGIC, _MOV_EXT, _MOV_MAGIC_WEAK} from "../video/mov.js";
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
	converters       = dexState =>
	{
		const r = ["ffmpeg[outType:mp3]"];
		if(RUNTIME.asFormat!=="audio/quickTimeAudio")
		{
			const magicCount = _MOV_MAGIC.map(m => (dexState.hasMagics(m) ? 1 : 0)).sum();
			if(magicCount>1 || (magicCount===1 && !dexState.hasMagics(_MOV_MAGIC_WEAK)))
			{
				RUNTIME.forbidProgram.delete("qtflatt");
				r.push("qtflatt[chainAs:audio/quickTimeAudio]");
			}
		}

		return r;
	};
}
