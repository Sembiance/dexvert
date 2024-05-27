import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class callFunction extends Program
{
	website = "https://github.com/Sembiance/dexvert";
	unsafe  = true;
	flags   = {
		formatid    : "Specify which formatid has the function to call",
		functionKey : "Specify which function key to apply"
	};
	exec = async r =>
	{
		const format = await import(path.join(import.meta.dirname, "..", "..", "format", `${r.flags.formatid}.js#${xu.randStr()}`));
		if(!format)
			return r.xlog.warn`Format [${r.flags.formatid}] not found`;

		const fun = format[r.flags.functionKey];
		if(!fun)
			return r.xlog.warn`Function [${r.flags.functionKey}] not found in format [${r.flags.formatid}]`;

		await fun({r});
	};
	allowDupOut = true;
	renameOut = false;
}
