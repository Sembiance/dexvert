import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {fileUtil} from "xutil";
import {detectPreRename} from "../../dexUtil.js";

export class ffprobeID extends Program
{
	website = "https://ffmpeg.org/";
	package = "media-video/ffmpeg";
	bin     = "ffprobe";
	loc     = "local";
	pre     = detectPreRename;
	args    = r => ["-v", "quiet", "-show_entries", "format=format_name,format_long_name", "-of", "default=noprint_wrappers=1:nokey=1", "-analyzeduration", "2000000", r.detectTmpFilePath];
	post    = async r =>
	{
		await fileUtil.unlink(r.detectTmpFilePath);

		r.meta.detections = [];

		const matchValue = r.stdout.trim() || "";
		if(matchValue?.length)
		{
			const matchParts = matchValue.split("\n");
			r.meta.detections.push(Detection.create({value : matchParts.length>1 ? `${matchParts[1]} (${matchParts[0]})` : matchParts[0], from : "ffprobeID", file : r.f.input}));
		}
	};
	renameOut = false;
}
