import {xu} from "xu";
import {Format} from "../../Format.js";

export class asymetrixToolbook extends Format
{
	name           = "Asymetrix ToolBook File";
	website        = "http://fileformats.archiveteam.org/wiki/Asymetrix_Toolbook";
	ext            = [".tbk", ".sbk"];
	forbidExtMatch = true;
	magic          = ["Asymetrix ToolBook", /^fmt\/(470|1795)( |$)/];
	notes          = xu.trim`
		Goal is to use the original ToolBook software to open and extract the files. Only version I could find is 3.0 which wouldn't open the sample files. Looking for a later version.
		Unfortunately, the files are version locked to specific engines according to: https://tb.sumtotalsystems.com/KBFiles/kb/ToolBook%20Knowledge%20Base.html?RuntimeEngines.html
		This would then require having to install multiple versions of ToolBook and trying each one to see if it can open and edit a given TBK file.`;
	converters     = ["strings"];
}
