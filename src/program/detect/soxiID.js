import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {fileUtil} from "xutil";

export class soxiID extends Program
{
	website = "http://sox.sourceforge.net";
	package = "media-sound/sox";
	bin     = "soxi";
	loc     = "local";
	pre = async r =>
	{
		// soxi will match against file extension which would be BAD since that would mean extensions get converted to stronger 'magic', so we copy it to a tmp file (with a random.tmp name) and run trid against that
		// HOWEVER, some formats are not 'checked' by soxi UNLESS the extension is set, so we allow certain extensions in
		const ALLOWED_EXTS =
		[
			".snd"		// audio/sounder
		];
		r.soxiTmpFilePath = await fileUtil.genTempPath(undefined, (ALLOWED_EXTS.includes(r.f.input.ext?.toLowerCase()) ? r.f.input.ext : undefined));
		try
		{
			if(await fileUtil.exists(r.inFile({absolute : true})))
				await Deno.copyFile(r.inFile({absolute : true}), r.soxiTmpFilePath);			// can't use a symlink as that changes the file type, hard link can't be used across different filesystems, so we have to copy. sad.
		}
		catch(err)
		{
			r.xlog.warn`Failed to copy file to tmp file for soxiID: ${err}`;
		}
	};

	args = r => ["-t", r.soxiTmpFilePath];
	post = async r =>
	{
		await fileUtil.unlink(r.soxiTmpFilePath);

		r.meta.detections = [];

		for(const line of r.stdout.trim().split("\n"))
		{
			if(line.trim().length)
				r.meta.detections.push(Detection.create({value : `soxi: ${line.trim()}`, confidence : 100, from : "soxiID", file : r.f.input}));
		}
	};
	renameOut = false;
}
