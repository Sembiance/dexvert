import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {C} from "../../C.js";

export class binwalkID extends Program
{
	website = "https://github.com/OSPG/binwalk";
	loc     = "local";
	exec    = async r =>
	{
		r.meta.detections = [];

		const result = await xu.fetch(`http://${C.BINWALK_SERVER_HOST}:${C.BINWALK_SERVER_PORT}/detect`, {json : {filePath : r.inFile({absolute : true})}, asJSON : true});
		if(result?.error)
			return r.xlog.error`binwalkID error: ${result.error}`;

		r.xlog.debug`binwalkID /detect result: ${result}`;

		for(const {offset, description} of result?.matches || [])
		{
			if(offset!==0)
				continue;

			r.meta.detections.push(Detection.create({value : description, confidence : 100, from : "binwalkID", file : r.f.input}));
		}
	};
	renameOut = false;
}
