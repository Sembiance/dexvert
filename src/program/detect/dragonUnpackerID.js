import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {C} from "../../C.js";

export class dragonUnpackerID extends Program
{
	website = "https://github.com/elbereth/DragonUnPACKer";
	loc     = "local";
	exec    = async r =>
	{
		r.meta.detections = [];

		const result = await xu.fetch(`http://${C.DRAGON_UNPACKER_HOST}:${C.DRAGON_UNPACKER_PORT}/detect`, {json : {filePath : r.flags.detectTmpFilePath}, asJSON : true});
		if(result?.error)
			return r.xlog.error`dragonUnpackerID error: ${result.error}`;

		for(const {formatType, gameName, matchType, extensions} of result || [])
		{
			if(matchType==="extension" && (!r.xlog || !r.xlog.atLeast("trace")))
				continue;

			const vals = [];
			vals.push(`dragon: ${formatType}`);
			vals.push(` - ${gameName}`);
			r.meta.detections.push(Detection.create({value : vals.join(""), from : "dragonUnpackerID", extensions : (extensions || []).sortMulti().map(v => `.${v.toLowerCase()}`), file : r.f.input}));
		}
	};
	renameOut = false;
}
