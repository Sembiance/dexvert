import {Program} from "../../Program.js";
import {encodeUtil} from "xutil";

function cleanMacFilename(fn)
{
	let match = null;
	do
	{
		match = (fn.match(/%(?<code>[A-Fa-f\d]{2})/) || {}).groups;
		if(match)
			fn = fn.replaceAll(`%${match.code}`, encodeUtil.MACOS_ROMAN_EXTENDED[Number.parseInt(match.code, 16)-128] || "□");	// eslint-disable-line no-param-reassign
	} while(match);

	return fn;
}

export class unar extends Program
{
	website   = "https://unarchiver.c3.cx/";
	package   = "app-arch/unar";
	flags   = {
		"mac" : "Set this flag to treat the files extracted as mac files and rename them with the MACOS_ROMAN_EXTENDED charset."
	};
	bin       = "unar";
	args      = r => [...(r.flags.filenameEncoding ? ["-e", r.flags.filenameEncoding] : []), "-f", "-D", "-o", r.outDir(), r.inFile()];
	
	// we normally wouldn't rename the output files at all, however when processing certain Mac files, it can produce the '\r' character which we want to replace with "↵" (we also replace "\n" just in case)
	// that's the only thing this method does, otherwise it leaves the output filenames alone
	// it is QUITE POSSIBLE that there are additional MacOS specific characters that's we'd want to replace here (as setting filenameEncoding above didn't help) but we'll have to wait and discover those
	// most Mac files don't got through here (from archive/macBinary), but rather deark
	renameOut = {
		alwaysRename : true,
		renamer      :
		[
			({fn, r}) => [(r.flags.mac ? cleanMacFilename(fn) : fn).replaceAll("\r", "↵").replaceAll("\n", "↵").replaceAll("\t", "⇥")]
		]
	};
}
