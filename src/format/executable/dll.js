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
	magic        = [
		// general DLL type
		"Win32 Dynamic Link Library", "PE32 executable (DLL)", "PE32+ executable (DLL)", /^MS-DOS executable, NE for MS Windows .*\(DLL or font\)/, "PE Unknown PE signature 0 (DLL)",
		"OLE Custom / ActiveX Control", "OLE Custom Control",

		// specific DLL types
		"Photoshop filter plug-in", "PhotoShop plug-in", "NT5 Migrate DLL", "DLL PowerBASIC PB/DLL 6.x", "OllyDbg plugin", "Borland component", "Python Dynamic module", "Adobe Acrobat Reader Plugin", "BRender Device Driver",	// BR not a typo
		"Borland Package Library", "WinAmp 2.x Input plugin", "WinAmp 2.x Output plugin", "Winconv conversion module",  "Generic .NET DLL/Assembly", "FileMaker Pro 32-bit plug-in", "MS Flight Simulator Gauge", "VirtualDub Filter Plug-in",
		"Pixia filter plugin", "Psycle plugin", "Ultimate Paint Graphics Editor plugin/effect", "Miranda IM plugin", "ACDSee plugin", "DLL PowerBASIC", "Microsoft Input Method Editor", "Quintessential Player input plugin",
		"ZoneLabs Zone Alarm data", "Aston Shell plugin", /^foobar 2000 (Diskwriter output|Input|generic) component/, "Take Command plugin", "MATLAB Windows 32bit compiled function", "JAJC plugin", "DeliPlayer player plugin",
		"Microsoft Windows Defender Virus Definition Module", "DeliPlayer genie", "Classic/Open-Shell Windows style skin", "ZX Spin Render Plugin", "AkelPad plugin", "Microsoft Resource Library (x64)", "Maya plug-in (generic)",
		"OLE Custom / ActiveX Control (32bit)", "OLE Custom Control (16bit)", "Imagine for Windows Texture"
	];
	priority     = this.PRIORITY.LOW;
	metaProvider = ["winedump"];

	// We throw DLLs at deark and 7z which can often extract various embedded cursors, icons and images
	converters = dexState =>
	{
		if(BAD_FILENAMES_TO_SKIP_ENTIRELY.includes(dexState.original?.input?.base?.toLowerCase()))
		{
			dexState.xlog.warn`SKIPPING THIS FILE ENTIRELY because it's a known filename that is intentionally skipped!`;
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
