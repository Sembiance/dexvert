import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";

export class disktype extends Program
{
	website = "http://disktype.sourceforge.net";
	package = "sys-block/disktype";
	bin     = "disktype";
	loc     = "local";
	args    = r => [r.inFile()];
	post    = r =>
	{
		r.meta.detections = [];

		const magic = [];
		for(const line of r.stdout.trim().split("\n"))
		{
			if(["---", "Regular file", "Block device", "Character device", "FIFO", "Socket", "Unknown kind"].some(v => line.startsWith(v)))
				continue;

			// I commented this out because I've only encountered it once and in theory this could acidentally filter files that happen to be named the same as the magic, so I leave it for now but can easily uncomment later
			//if(line.trim()===r.f.input.base)	// skip if the magic is exactly equal to the filename (rare but it happens: http://dev.discmaster2.textfiles.com/admin/item?itemid=12646)
			//	continue;

			if(line.trim().length)
				magic.push(line.trim());
		}

		if(magic.length)
			r.meta.detections.push(Detection.create({value : magic.join(" "), confidence : 100, from : "disktype", file : r.f.input}));
	};
	renameOut = false;
}
