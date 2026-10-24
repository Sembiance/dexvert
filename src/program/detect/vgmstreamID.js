import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {C} from "../../C.js";

export class vgmstreamID extends Program
{
	website = "https://github.com/vgmstream/vgmstream";
	loc     = "local";
	exec    = async r =>
	{
		r.meta.detections = [];

		const result = await xu.fetch(`http://${C.VGMSTREAM_HOST}:${C.VGMSTREAM_PORT}/detect`, {json : {filePath : r.inFile({absolute : true})}, asJSON : true});	// r.flags.detectTmpFilePath
		if(result?.error)
			return r.xlog.error`vgmstreamID error: ${result.error}`;

		r.xlog.debug`vgmstreamID /detect result: ${result}`;

		for(const {formatid, name} of result?.detections || [])
			r.meta.detections.push(Detection.create({value : `vgmstream: ${formatid} - ${name}`, from : "vgmstreamID", file : r.f.input}));
	};
	renameOut = false;
}
