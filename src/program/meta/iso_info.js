import {Program} from "../../Program.js";

export class iso_info extends Program
{
	website = "https://www.gnu.org/software/libcdio";
	package = "dev-libs/libcdio";
	bin     = "iso-info";
	args    = r => [r.inFile()];
	post    = r =>
	{
		r.stdout.trim().split("\n").forEach(line =>
		{
			const {key, val} = (line.trim().match(/^(?<key>[^:]+)\s*:\s*(?<val>.+)$/) || {groups : {}}).groups;
			if(key && key==="ISO 9660 image")
				r.meta.isISO = true;
			if(key && val && !["ISO 9660 image", "iso-info", "++ WARN"].some(v => key.trim().startsWith(v)))
				r.meta[key.trim().toCamelCase()] = val.trim();
		});
	};
	renameOut = false;
}
