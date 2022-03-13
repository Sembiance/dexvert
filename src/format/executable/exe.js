import {Format} from "../../Format.js";

export class exe extends Format
{
	name    = "MS-DOS/Windows Executable";
	website = "http://fileformats.archiveteam.org/wiki/EXE";
	ext     = [".exe"];
	magic   = [
		"Generic Win/DOS Executable", "DOS Executable Generic", /MS-DOS [Ee]xecutable/, /^Win\d\d Executable/, /compressed DOS Executable$/, "DOS Executable (alternate ZM id)", "16bit DOS EXE PKLite compressed",
		"PE32 executable", /^Win\d\d Executable/, "Win16 NE executable"
	];
	priority     = this.PRIORITY.LOW;
	metaProvider = ["winedump"];

	pre = dexState =>
	{
		// If we have meta from winedump and it's a DLL file, then delete the meta which will cause no converters to run
		if((dexState.meta?.fileheader?.characteristics || []).includes("DLL"))
			dexState.meta = {};
	};

	// We throw MSDOS/Win EXESs at deark and 7z which can often extract various embedded cursors, icons and images
	converters = dexState => (Object.keys(dexState.meta).length>0 ? ["sevenZip[type:PE][rsrcOnly]", "deark"] : []);

	post = dexState =>
	{
		if(Object.keys(dexState.meta).length>0)
			dexState.processed = true;
	};
}

// Borland Delphi EXE/DLL extractor in sandbox/app/IDR/
// It's not really needed though, as the delphi forms are usually Resources that get extracted by sevenZip and then handled by my borlandDelphiForm program

// Alternative EXE meta info identifier: https://github.com/horsicq/Detect-It-Easy
