import {Program} from "../../Program.js";

export class ffprobe extends Program
{
	website = "https://ffmpeg.org/";
	package = "media-video/ffmpeg";
	bin     = "ffprobe";
	args    = r => ["-show_streams", "-show_format", r.inFile()];
	post    = r =>
	{
		let seenFormatSection = false;
		r.stdout.trim().split("\n").forEach(line =>
		{
			if(line.trim()==="[FORMAT]")
			{
				seenFormatSection = true;
				return;
			}

			if(!seenFormatSection)
				return;
			
			const tag = (line.trim().match(/^(?<tag>TAG:)?(?<key>[^=]+)=(?<value>.+)$/) || {groups : {}}).groups;
			if(tag.key && tag.value && tag.key.trim().length>0 && tag.value.trim().length>0)
			{
				const key = tag.key.trim().replaceAll("_", " ").toCamelCase();
				if(["size", "probeScore", "filename"].includes(key))
					return;
				
				const value = tag.value.trim();
				if(value==="N/A")
					return;

				r.meta[key] = ["bitRate", "duration", "startTime", "nbStreams", "nbPrograms"].includes(key) ? +value : value;
			}
		});
	};
	renameOut = false;
}
