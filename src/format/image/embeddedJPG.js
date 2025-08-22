import {Format} from "../../Format.js";

export class embeddedJPG extends Format
{
	name       = "Embedded JPEG File";
	magic      = [
		// generic
		"JPEG based file :pmp:",
		
		// app specific
		"DELFTship ship"
	];
	priority   = this.PRIORITY.LOWEST;
	fallback   = true;
	converters = ["nconvert[format:pmp]"];
	verify     = ({meta}) => !Object.hasOwn(meta, "colorCount") || meta.colorCount>1;
}
