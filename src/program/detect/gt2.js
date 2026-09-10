import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {C} from "../../C.js";

export class gt2 extends Program
{
	website = "https://github.com/phax/gt";
	loc     = "local";
	exec    = async r =>
	{
		r.meta.detections = [];

		const result = await xu.fetch(`http://${C.GT2_HOST}:${C.GT2_PORT}/detect`, {json : {filePath : r.flags.detectTmpFilePath}, asJSON : true});
		if(result?.error)
			return r.xlog.error`gt2 error for ${r.f.input.pretty()}: ${result.error}`;

		for(const {format, offset} of result || [])
		{
			if(offset===0)
				r.meta.detections.push(Detection.create({value : format, from : "gt2", file : r.f.input, weak : format.startsWith("Kopftext:")}));
		}
	};
	renameOut = false;
}
