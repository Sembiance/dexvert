import {Format} from "../../Format.js";

export class exe extends Format
{
	name    = "MS-DOS/Windows Executable";
	website = "http://fileformats.archiveteam.org/wiki/EXE";
	ext     = [".exe"];
	magic   = [
		"Generic Win/DOS Executable", "DOS Executable", /MS-DOS [Ee]xecutable/, /^Win\d\d Executable/, /compressed DOS Executable$/, "DOS Executable (alternate ZM id)", "16bit DOS EXE PKLite compressed",
		"PE32 executable", /^Win\d\d Executable/, "Win16 NE executable", /^NSIS$/, /^Ist eine ausf.hrbare (Win 3\.x|DOS|Win32) Datei$/, /^fmt\/899( |$)/, /^x-fmt\/(409|410)( |$)/];
	priority     = this.PRIORITY.LOW;
	metaProvider = ["winedump"];

	pre = dexState =>
	{
		// If we have meta from winedump and it's a DLL file, then delete the meta which will cause no converters to run
		if((dexState.meta?.fileheader?.characteristics || []).includes("DLL"))
			Object.clear(dexState.meta);
	};

	// We throw MSDOS/Win EXESs at various programs to try and get something useful out of them like embedded director files, cursors, icons, images, etc
	// Could also 'decompress' packed EXEs by adding "deark[module:exepack]" but that doesn't really provide us with any actual content, so meh.
	converters = dexState => (Object.keys(dexState.meta).length>0 ? [
		// Is it just a ZIP file of some sort?
		"sevenZip[type:zip]",
		
		// What about an NSIS installer?
		"sevenZip[type:nsis]",
		"unar[type:nsis]",

		// Is it a Projector executable hiding a director file?
		"director_files_extract",

		// generic installer extractor
		"cmdTotal[wcx:InstExpl.wcx]",

		// Try some general EXE extractors
		"sevenZip[type:PE][rsrcOnly]",
		"deark[module:exe]"
	] : []);

	post = dexState =>
	{
		if(Object.keys(dexState.meta).length>0)
			dexState.processed = true;
	};
}

// Borland Delphi EXE/DLL extractor in sandbox/app/IDR/
// It's not really needed though, as the delphi forms are usually Resources that get extracted by sevenZip and then handled by my borlandDelphiForm program
