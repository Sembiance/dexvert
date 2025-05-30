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
		const data = xu.parseJSON(r.stdout.trim(), undefined, {fixInvalidControlChars : true});	// lsar can output invalid JSON (archive/diskDoubler/VocaBuilder© File.sea)
		if(!data || !data?.lsarFormatName)
			return;
		
		if(data.lsarConfidence===0 && !data.lsarContents?.length)
			return;

		const confidence = !data.lsarContents?.length ? 1 : (data.lsarConfidence || 1)*100;
		if(data.lsarInnerFormatName)
			r.meta.detections.push(Detection.create({value : data.lsarInnerFormatName, confidence : Math.min(100, confidence+1), from : "lsar", file : r.f.input}));
		r.meta.detections.push(Detection.create({value : data.lsarFormatName, confidence, from : "lsar", file : r.f.input}));
	};
	renameOut = false;
}
