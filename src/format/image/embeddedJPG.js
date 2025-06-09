import {Format} from "../../Format.js";

export class embeddedJPG extends Format
{
	name       = "Embedded JPEG File";
	magic      = ["JPEG based file :pmp:"];
	priority   = this.PRIORITY.LOWEST;
	fallback   = true;
	converters = ["nconvert[format:pmp]"];
	verify     = ({meta}) => !Object.hasOwn(meta, "colorCount") || meta.colorCount>1;
}
