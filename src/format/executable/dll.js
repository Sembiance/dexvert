import {Format} from "../../Format.js";

export class dll extends Format
{
	name         = "Microsoft Windows Dynmic Link Library";
	ext          = [".dll"];
	forbiddenExt = [".exe"];
	magic        = ["Win32 Dynamic Link Library", "PE32 executable (DLL)", "MS-DOS executable, NE for MS Windows 3.x (DLL or font)", "PE Unknown PE signature 0 (DLL)"];
	metaProvider = ["winedump"];

	// We throw DLLs at deark and 7z which can often extract various embedded cursors, icons and images
	converters = dexState => (Object.keys(dexState.meta).length>0 ? ["sevenZip[type:PE][rsrcOnly]", "deark"] : []);
	post  = dexState =>
	{
		if(Object.keys(dexState.meta).length>0)
			dexState.processed = true;
	};
}
