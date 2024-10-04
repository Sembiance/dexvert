import {Format} from "../../Format.js";

export class riscOSFontMetrics extends Format
{
	name         = "RiscOS Font Metrics";
	magic        = ["Acorn RISC OS font (v2)"];
	filename     = [/^intmetric$/i];
	weakFilename = true;
	auxFiles     = (inputFile, otherFiles) => otherFiles.filter(otherFile => otherFile.base.toLowerCase().startsWith("outlines"));
	untouched    = true;
}
