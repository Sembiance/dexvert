import {Format} from "../../Format.js";

export class cab extends Format
{
	name     = "Cabinet";
	website  = "http://fileformats.archiveteam.org/wiki/Cabinet";
	ext      = [".cab"];
	filename = [/^cabinet$/, /^_cabinet$/i];
	magic    = [
		// general cab
		/^Microsoft Cabinet [Aa]rchive/, "CAB Archiv gefunden", "Archive: Microsoft Cabinet File", "Self-extracting CAB", "Win32 MS Cabinet Self-Extractor",  "application/vnd.ms-cab-compressed", /^CAB$/, /^fmt\/1839( |$)/, /^x-fmt\/(216|414)( |$)/,
		
		// app specific cabs
		"IncrediMail data (generic)", "IncrediMail Animation", "IncrediMail letter/ecard Flavor", "IncrediMail Image", "IncrediMail sound", "IncrediMail Notifier", "IncrediMail Skin",
		"Diagnostic Cabinet", "Skin / Theme for Pocket PC PDAs", "Windows Device Metadata", "Microsoft Vista Sidebar Gadget (CAB", "InfoPath Dynamic Form - Template",
		/^fmt\/987( |$)/,

		// installer related cabs
		"Microsoft Update - Self Extracting Cabinet", "Microsoft Windows CE installation Cabinet Archive", "Windows Installer Merge Module (CAB)", "MS generic-sfx Cabinet File Unpacker",
		"Installer: PackageForTheWeb", "Installer: Wise Installer[CAB]", "Installer: Windows Installer", "Installer: Advanced Installer"
	];
	auxFiles = (input, otherFiles) =>
	{
		// include any other files named the same as the input file but with a different extension so long as the extension is a number
		const parts = otherFiles.filter(file => file.name.toLowerCase()===input.name.toLowerCase() && file.ext.match(/^\.\d+$/));
		return parts?.length ? parts : false;
	};
	untouched = dexState => dexState.id?.auxFiles?.length && dexState.original?.input?.ext!==".1";	// If we do have aux files, then we are a multi-part cabinet and we need to only process the first part as it gets everything
	keepFilename = true;
	converters   = ["cabextract", "sqc", "deark[module:cab]", "izArc", "UniExtract"];
}
