import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";

export class xdgMime extends Program
{
	website = "https://www.freedesktop.org/wiki/Software/xdg-utils/";
	package = "x11-misc/xdg-utils";
	bin     = "xdg-mime";
	loc     = "local";
	args    = r => ["query", "filetype", r.inFile()];
	post    = r =>
	{
		const mimeType = r.stdout.trim() || "";
		r.meta.detections = [];
		if(mimeType?.length && !["application/octet-stream"].includes(mimeType))
			r.meta.detections.push(Detection.create({value : mimeType, from : "xdgMime", file : r.f.input}));
	};
	notes     = "xdg-mime mostly only works on file extension, which isn't useful to us, so we don't actually include this in the detection process";
	renameOut = false;
}
