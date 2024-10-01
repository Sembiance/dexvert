import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {fileUtil} from "xutil";

export class ffprobeID extends Program
{
	website = "https://ffmpeg.org/";
	package = "media-video/ffmpeg";
	bin     = "ffprobe";
	loc     = "local";
	pre     = async r =>
	{
		// ffprobeID will match against file extension which would be BAD since that would mean extensions get converted to stronger 'magic', so we copy it to a tmp file (with a random.tmp name) and run trid against that
		r.ffprobeIDTempFilePath = await fileUtil.genTempPath();
		try
		{
			if(await fileUtil.exists(r.inFile({absolute : true})))
				await Deno.copyFile(r.inFile({absolute : true}), r.ffprobeIDTempFilePath);			// can't use a symlink as that changes the file type, hard link can't be used across different filesystems, so we have to copy. sad.
		}
		catch(err)
		{
			r.xlog.warn`Failed to copy file to tmp file for ffprobeID: ${err}`;
		}
	};
	args = r => ["-v", "quiet", "-show_entries", "format=format_name,format_long_name", "-of", "default=noprint_wrappers=1:nokey=1", "-analyzeduration", "2000000", r.ffprobeIDTempFilePath];
	post = async r =>
	{
		await fileUtil.unlink(r.ffprobeIDTempFilePath);

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
