import {Format} from "../../Format.js";
import {path} from "std";

export class symlink extends Format
{
	name      = "symlink";
	untouched = true;
	notes     = "This format is a hardcoded match at the beginning of identify.js";
	meta      = async (inputFile, dexState) =>
	{
		const m = {};

		const linkPath = await Deno.readLink(dexState.original.input.absolute);
		if(linkPath?.length)
		{
			m.linkPath = linkPath;
			if(m.linkPath.startsWith("/"))
				m.linkPathRelative = path.relative(dexState.original.input.dir, m.linkPath);
		}

		return m;
	};
}
