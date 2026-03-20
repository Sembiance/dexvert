import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {C} from "../../C.js";

export class GARbroID extends Program
{
	website = "https://github.com/shiikwi/GARbro";
	loc     = "local";
	exec    = async r =>
	{
		r.meta.detections = [];

		const result = await xu.fetch(`http://${C.GARBRO_HOST}:${C.GARBRO_PORT}/detect`, {json : {filePath : r.inFile({absolute : true})}, asJSON : true});	// r.flags.detectTmpFilePath
		if(result?.error)
			return r.xlog.error`GARbroID error: ${result.error}`;

		r.xlog.debug`GARbroID /detect result: ${result}`;

		for(const {formatType, tag, description, extensions, matchTypes} of result?.detections || [])
		{
			const vals = [];
			vals.push(formatType);
			vals.push(` (${tag}) - ${description}`);
			r.meta.detections.push(Detection.create({value : vals.join(""), from : "GARbroID", extensions : (extensions || []).sortMulti(), weak : matchTypes.length===1 && matchTypes[0]==="heuristic", file : r.f.input}));
		}
	};
	renameOut = false;
}
