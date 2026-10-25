import {xu} from "xu";
import {Program} from "../../Program.js";

export class ffprobe extends Program
{
	website = "https://ffmpeg.org/";
	package = "media-video/ffmpeg";
	flags   = {
		libre       : "Use librempegprobe instead of ffprobe"
	};
	bin  = r => (r.flags.libre ? "librempegprobe" : "ffprobe");
	args = r => ["-v", "error", "-show_packets", "-show_streams", "-show_format", "-of", "json", r.inFile()];
	post = r =>
	{
		const probeInfo = xu.parseJSON(r.stdout);
		if(!probeInfo)
			return;
		
		const tagTypes =
		{
			stream :
			{
				"width"           : {type : "number"},
				"height"          : {type : "number"},
				"nb_frames"       : {type : "number", rename : "frameCount"},
				"duration"        : {type : "number", rename : "streamDuration", convert : v => +v*xu.SECOND},
				"codec_name"      : {type : "string"},
				"codec_long_name" : {type : "string"},
				"avg_frame_rate"  : {type : "divide", rename : "fps", fallback : "r_frame_rate"}
			},
			format :
			{
				"nb_streams"       : {type : "number", rename : "streamCount"},
				"nb_programs"      : {type : "number", rename : "programCount"},
				"start_time"       : {type : "number"},
				"duration"         : {type : "number", rename : "formatDuration", convert : v => +v*xu.SECOND},
				"bit_rate"         : {type : "number"},
				"format_name"      : {type : "string"},
				"format_long_name" : {type : "string"}
			}
		};

		for(const [sectionName, sectionTags] of Object.entries(tagTypes))
		{
			const section = sectionName==="stream" ? (probeInfo.streams || []).find(o => o.codec_type==="video") : probeInfo[sectionName];
			if(!section || !Object.isObject(section))
				continue;

			for(const [tag, {type, rename, convert, fallback}] of Object.entries(sectionTags))
			{
				if(Object.hasOwn(section, tag))
				{
					const key = rename || tag.replaceAll("_", " ").toCamelCase();
					const getValue = tagValue =>
					{
						const value = type==="number" ? +tagValue : (type==="divide" ? (+tagValue.split("/")[0]/+tagValue.split("/")[1]) : tagValue);
						return convert ? convert(value) : value;
					};
					r.meta[key] = getValue(section[tag]);
					if(["number", "divide"].includes(type) && isNaN(r.meta[key]))
					{
						delete r.meta[key];
						if(fallback)
							r.meta[key] = getValue(section[fallback]);
					}
				}
			}
		}

		// prefer format duration over stream duration
		if(r.meta.formatDuration || r.meta.streamDuration)
			r.meta.duration = r.meta.formatDuration || r.meta.streamDuration;
		delete r.meta.formatDuration;
		delete r.meta.streamDuration;

		// fallback to calculating duration from fps and frameCount if duration is not provided
		if(!r.meta.duration && r.meta.fps && r.meta.frameCount)
			r.meta.duration = (r.meta.frameCount/r.meta.fps)*xu.SECOND;

		// otherwise check packets
		if(!r.meta.duration && probeInfo.packets?.length)
			r.meta.duration = (probeInfo.packets.map(p => (+p.pts_time)+(+(p.duration_time || 0))).max()-probeInfo.packets.map(o => +o.pts_time).min())*xu.SECOND;

		if(isNaN(r.meta.duration))
			delete r.meta.duration;
	};
	renameOut = false;
}
