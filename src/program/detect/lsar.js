import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";

export class lsar extends Program
{
	website = "https://github.com/incbee/Unarchiver";
	package = "app-arch/unar";
	bin     = "lsar";
	loc     = "local";
	args    = r => ["-j", r.inFile()];
	post    = r =>
	{
		r.meta.detections = [];
		const data = xu.parseJSON(r.stdout.trim());
		if(!data || !data?.lsarFormatName)
			return;
		
		if(data.lsarConfidence===0 && !data.lsarContents?.length)
			return;

		if(data.lsarInnerFormatName)
			r.meta.detections.push(Detection.create({value : data.lsarInnerFormatName, confidence : Math.min(100, ((data.lsarConfidence || 1)*100)+1), from : "lsar", file : r.f.input}));
		r.meta.detections.push(Detection.create({value : data.lsarFormatName, confidence : (data.lsarConfidence || 1)*100, from : "lsar", file : r.f.input}));
	};
	renameOut = false;
}
