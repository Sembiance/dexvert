import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {C} from "../../C.js";

export class trid extends Program
{
	website = "https://mark0.net/soft-trid-e.html";
	loc     = "local";
	exec    = async r =>
	{
		r.meta.detections = [];

		const result = await xu.fetch(`http://${C.TRID_SERVER_HOST}:${C.TRID_SERVER_PORT}/detect`, {json : {filePath : r.inFile({absolute : true})}, asJSON : true});
		if(result?.error)
			return r.xlog.error`trid /detect error: ${result.error}`;

		r.xlog.debug`trid /detect result: ${result}`;
		
		for(const {percent, extension, fileType} of result?.matches || [])
		{
			const tridMatch = {from : "trid", confidence : percent, value : fileType, file : r.f.input};
			tridMatch.extensions = (extension.includes("/") ? extension.split("/") : [extension]).map(ext => ext.toLowerCase()).map(ext => (ext.charAt(0)==="." ? "" : ".") + ext);
			r.meta.detections.push(Detection.create(tridMatch));
		}
	};
	renameOut = false;
}
