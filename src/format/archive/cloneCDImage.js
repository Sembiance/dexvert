import {Format} from "../../Format.js";

export class cloneCDImage extends Format
{
	name       = "CloneCD Image";
	ext        = [".img"];
	auxFiles   = (input, otherFiles) => otherFiles.filter(file => file.base.toLowerCase()===`${input.name.toLowerCase()}.ccd`);
	priority   = this.PRIORITY.LOW;
	converters = ["aaru"];
}
