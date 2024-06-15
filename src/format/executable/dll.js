import {Format} from "../../Format.js";

const BAD_FILENAMES_TO_SKIP_ENTIRELY =
[
	"msimsg.dll"	// Produces 6,000+ sub files and often has multiple copies of itself
];

export class dll extends Format
{
	name         = "Microsoft Windows Dynamic Link Library";
	website      = "http://fileformats.archiveteam.org/wiki/Dynamic-link_library_(Windows)";
	ext          = [".dll"];
	forbiddenExt = [".exe"];
	magic        = ["Win32 Dynamic Link Library", "PE32 executable (DLL)", "PE32+ executable (DLL)", /^MS-DOS executable, NE for MS Windows .*\(DLL or font\)/, "PE Unknown PE signature 0 (DLL)"];
	priority     = this.PRIORITY.LOW;
	metaProvider = ["winedump"];

	// We throw DLLs at deark and 7z which can often extract various embedded cursors, icons and images
	converters = dexState =>
	{
		if(BAD_FILENAMES_TO_SKIP_ENTIRELY.includes(dexState.original?.input?.base?.toLowerCase()))
		{
			dexState.processed = true;
			return [];
		}

		return (Object.keys(dexState.meta).length>0 ? [
			// first make sure there it's not a Projector file with a director file hidden in it, then we want to extract it for sure
			"director_files_extract",

			// otheriwse just extract whatever resources we can
			"sevenZip[type:PE][rsrcOnly]",
			"deark[module:exe]"] : []);
	};
	post  = dexState =>
	{
		if(Object.keys(dexState.meta).length>0)
			dexState.processed = true;
	};
}
