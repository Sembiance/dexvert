import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";

export class binwalkID extends Program
{
	website = "https://github.com/OSPG/binwalk";
	package = "app-misc/binwalk";
	bin     = "binwalk";
	loc     = "local";
	args    = r => ["--length=512", r.inFile()];
	post    = r =>
	{
		r.meta.detections = [];

		const magic = [];
		for(const line of r.stdout.trim().split("\n"))
		{
			if(!line.trim().length)
				continue;

			if(["---", "DECIMAL"].some(v => line.startsWith(v)))
				continue;

			const {offset, magicValue} = line.match(/^(?<offset>\d+)\s+\S+\s+(?<magicValue>.+)$/)?.groups || {};
			if((+offset)===0 && magicValue?.trim().length)
				magic.push(magicValue.trim());
		}

		if(magic.length)
			r.meta.detections.push(Detection.create({value : magic.join(" "), confidence : 100, from : "binwalkID", file : r.f.input}));
	};
	renameOut = false;
}
