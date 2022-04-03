import {Program} from "../../Program.js";

export class pdfinfo extends Program
{
	website = "https://poppler.freedesktop.org/";
	package = "app-text/poppler";
	bin     = "pdfinfo";
	args    = r => [r.inFile()];
	post    = r =>
	{
		const meta = {};
	
		const NUMS = ["pages", "pagerot"];
		const BOOLS = ["tagged", "userproperties", "suspects", "javascript", "encrypted", "optimized"];
		r.stdout.trim().split("\n").filter(v => !!v).forEach(infoLine =>
		{
			const infoProps = (infoLine.trim().match(/^(?<name>[^:]+):\s+(?<val>.+)$/) || {})?.groups;
			if(!infoProps)
				return;

			const propKey = infoProps.name.toLowerCase().replaceAll(" ", "");
			if(propKey==="filesize")
				return;

			meta[propKey] = NUMS.includes(propKey) ? +infoProps.val : (BOOLS.includes(propKey) ? infoProps.val==="yes" : infoProps.val);
		});

		Object.assign(r.meta, meta);
	};
	renameOut = false;
}
