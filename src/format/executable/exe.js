import {Format} from "../../Format.js";

export class exe extends Format
{
	name    = "MS-DOS/Windows Executable";
	website = "http://fileformats.archiveteam.org/wiki/EXE";
	ext     = [".exe"];
	magic   = [
		"Generic Win/DOS Executable", "DOS Executable Generic", /MS-DOS [Ee]xecutable/, /^Win\d\d Executable/, /compressed DOS Executable$/, "DOS Executable (alternate ZM id)", "16bit DOS EXE PKLite compressed",
		"PE32 executable", /^Win\d\d Executable/, "Win16 NE executable", /^fmt\/899( |$)/, /^x-fmt\/(409|410)( |$)/];
	priority     = this.PRIORITY.LOW;
	metaProvider = ["winedump"];

	pre = dexState =>
	{
		// If we have meta from winedump and it's a DLL file, then delete the meta which will cause no converters to run
		if((dexState.meta?.fileheader?.characteristics || []).includes("DLL"))
			Object.clear(dexState.meta);
	};

	// We throw MSDOS/Win EXESs at deark and 7z which can often extract various embedded cursors, icons and images
	// We first try to extract as a ZIP file before resorting to processing as an executable
	// Could also 'decompress' packed EXEs by adding "deark[module:exepack]" but that doesn't really provide us with any actual content, so meh.
	converters = dexState => (Object.keys(dexState.meta).length>0 ? ["sevenZip[type:zip]", "sevenZip[type:PE][rsrcOnly]", "deark"] : []);

	post = dexState =>
	{
		if(Object.keys(dexState.meta).length>0)
			dexState.processed = true;
	};
}

// Borland Delphi EXE/DLL extractor in sandbox/app/IDR/
// It's not really needed though, as the delphi forms are usually Resources that get extracted by sevenZip and then handled by my borlandDelphiForm program

// Alternative EXE meta info identifier: https://github.com/horsicq/Detect-It-Easy
