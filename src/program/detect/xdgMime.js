import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {fileUtil} from "xutil";

export class xdgMime extends Program
{
	website = "https://www.freedesktop.org/wiki/Software/xdg-utils/";
	package = "x11-misc/xdg-utils";
	bin     = "xdg-mime";
	loc     = "local";

	// FAILURE NOTE: In Jan 2025, Gentoo updated xdg-utils to make the 'perl' flag optional which cause it not to install dev-perl/File-MimeInfo (mimetype command) which then caused xdg-mime to not identify some files such as: test/sample/text/advancedStreamRedirector/beck.asx
	// I added +perl to my package.use dexvert file and that fixes it, but making a note here just in case something similar happens in the future
	// I think this is because the /usr/share/mime/* files change when that perl package is installed that causes xdg-mime (and also mimetype command) to properly pick up different file types
	pre = async r =>
	{
		// xdg-mime will match against file extension which would be BAD since that would mean extensions get converted to stronger 'magic', so we copy it to a tmp file (with a random.tmp name) and run trid against that
		r.xdgMimeTmpFilePath = await fileUtil.genTempPath();
		try
		{
			if(await fileUtil.exists(r.inFile({absolute : true})))
				await Deno.copyFile(r.inFile({absolute : true}), r.xdgMimeTmpFilePath);			// can't use a symlink as that changes the file type, hard link can't be used across different filesystems, so we have to copy. sad.
		}
		catch(err)
		{
			r.xlog.warn`Failed to copy file to tmp file for xdgMime: ${err}`;
		}
	};

	args = r => ["query", "filetype", r.xdgMimeTmpFilePath];
	post = async r =>
	{
		await fileUtil.unlink(r.xdgMimeTmpFilePath);

		r.meta.detections = [];

		const mimeType = r.stdout.trim() || "";
		if(mimeType?.length && !["application/octet-stream", "text/plain"].includes(mimeType))
			r.meta.detections.push(Detection.create({value : mimeType, from : "xdgMime", file : r.f.input}));
	};
	renameOut = false;
}
