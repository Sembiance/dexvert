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
		const data = xu.parseJSON(r.stdout.trim());
		if(!data || !data?.lsarFormatName)
		{
			r.meta.detections = [];
			return;
		}
		
		if(data.lsarConfidence===0 && !data.lsarContents?.length)
		{
			r.meta.detections = [];
			return;
		}

		r.meta.detections = [Detection.create({value : data.lsarFormatName, confidence : (data.lsarConfidence || 1)*100, from : "lsar", file : r.f.input})] ;
	};
	renameOut = false;
}
