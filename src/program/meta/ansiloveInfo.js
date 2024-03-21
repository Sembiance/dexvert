import {xu} from "xu";
import {Program} from "../../Program.js";
import {dateFormat, dateParse} from "std";

export class ansiloveInfo extends Program
{
	website = "https://www.ansilove.org/";
	package = "media-gfx/ansilove";
	bin     = "ansilove";
	args    = r => ["-s", r.inFile()];
	post    = r =>
	{
		const meta = {};
	
		r.stdout.trim().split("\n").filter(v => !!v).forEach(infoLine =>
		{
			const infoProps = (infoLine.trim().match(/^(?<name>[^:]+):\s+(?<val>.+)$/) || {})?.groups;
			if(!infoProps)
				return;

			const propKey = infoProps.name.toLowerCase().replaceAll(" ", "");
			meta[propKey] = propKey==="date" ? dateFormat(dateParse(`${infoProps.val} 00:00:01`, "yyyyMMdd HH:mm:ss"), "yyyy-MM-dd") : infoProps.val;
		});

		Object.assign(r.meta, meta);
	};
	renameOut = false;
}
