import {Format} from "../../Format.js";

export class riscOSFont extends Format
{
	name         = "RiscOS Font";
	magic        = ["RISC OS Outline Font", /^RISC OS (outline|1bpp|4bpp) font data/];
	filename     = [/^outlines/i];
	weakFilename = true;
	keepFilename = true;
	auxFiles     = (inputFile, otherFiles) =>
	{
		const metricsFiles = otherFiles.filter(otherFile => otherFile.base.toLowerCase().startsWith("intmetric"));
		return metricsFiles?.length ? metricsFiles : false;
	};
	converters = ["acorn2sfd"];
}
