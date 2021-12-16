import {Program} from "../../Program.js";

export class otfinfo extends Program
{
	website = "http://www.lcdf.org/type/#typetools";
	package = "app-text/lcdf-typetools";
	bin     = "otfinfo";
	args    = r => ["-i", r.inFile()];
	post    = r =>
	{
		const meta = {};
		r.stdout.trim().split("\n").filter(v => !!v).forEach(line =>
		{
			const props = (line.trim().match(/^(?<name>[^:]+):\s+(?<val>.+)$/) || {}).groups;
			if(!props)
				return;

			meta[props.name.toCamelCase().replaceAll(" ", "").trim()] = props.val.trim();
		});

		Object.assign(r.meta, meta);
	};
	renameOut = false;
}
