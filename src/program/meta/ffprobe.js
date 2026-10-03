import {xu} from "xu";
import {Program} from "../../Program.js";

export class ffprobe extends Program
{
	website = "https://ffmpeg.org/";
	package = "media-video/ffmpeg";
	flags   = {
		libre       : "Use librempegprobe instead of ffprobe",
		countFrames : "Count the number of frames in the input file"
	};
	bin  = r => (r.flags.libre ? "librempegprobe" : "ffprobe");
	args = r => ["-v", "error", ...(r.flags.countFrames ? ["-select_streams", "v:0", "-count_frames", "-show_entries", "stream=nb_read_frames"] : ["-show_streams", "-show_format"]), r.inFile()];
	post = r =>
	{
		let seenSectionHeader = false;
		r.stdout.trim().split("\n").forEach(line =>
		{
			if(line.trim()===(r.flags.countFrames ? "[STREAM]" : "[FORMAT]"))
			{
				seenSectionHeader = true;
				return;
			}

			if(!seenSectionHeader)
				return;
			
			const tag = (line.trim().match(/^(?<tag>TAG:)?(?<key>[^=]+)=(?<value>.+)$/) || {groups : {}}).groups;
			if(tag.key && tag.value && tag.key.trim().length>0 && tag.value.trim().length>0)
			{
				const key = tag.key.trim().replaceAll("_", " ").toCamelCase();
				if(["filename", "nbStreamGroups", "probeScore", "size"].includes(key))
					return;
				
				const value = tag.value.trim();
				if(value==="N/A")
					return;

				r.meta[key] = ["bitRate", "duration", "startTime", "nbStreams", "nbPrograms", "nbReadFrames"].includes(key) ? (key==="duration" ? (+value)*xu.SECOND : +value) : value;
				if(key==="startTime" && r.meta.startTime<0)
					r.meta.startTime = 0;
			}
		});
	};
	renameOut = false;
}
