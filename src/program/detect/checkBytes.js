import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";

export class checkBytes extends Program
{
	website        = "https://github.com/Sembiance/dexvert/tree/master/bin/checkBytes";

	bin = Program.binPath("checkBytes/checkBytes");
	loc = "local";

	args = r => [r.input.primary.rel]
	post = r =>
	{
		r.meta.detections = [];

		if(r.stdout.trim().length===0)
			return;
		
		r.meta.detections.push(Detection.create({value : r.stdout.trim(), from : "checkBytes", file : r.inputOriginal.primary}));
	}
}
