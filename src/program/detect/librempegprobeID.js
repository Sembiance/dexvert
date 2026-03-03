import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";

export class librempegprobeID extends Program
{
	website = "https://github.com/librempeg/librempeg";
	package = "media-video/librempeg";
	bin     = "librempegprobe";
	loc     = "local";
	args    = r => ["-v", "quiet", "-show_entries", "format=format_name,format_long_name", "-of", "default=noprint_wrappers=1:nokey=1", "-analyzeduration", "2000000", r.flags.detectTmpFilePath];
	post    = r =>
	{
		r.meta.detections = [];

		const matchValue = r.stdout.trim() || "";
		if(matchValue?.length)
		{
			const matchParts = matchValue.split("\n");
			r.meta.detections.push(Detection.create({value : matchParts.length>1 ? `${matchParts[1]} (${matchParts[0]})` : matchParts[0], from : "librempegprobeID", file : r.f.input}));
		}
	};
	renameOut = false;
}
