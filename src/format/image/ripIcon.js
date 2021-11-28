import {Format} from "../../Format.js";

export class ripIcon extends Format
{
	name       = "RIP Icon";
	ext        = [".icn"];
	priority   = this.PRIORITY.HIGH;	// such a generic extension, but set high priority due to giving deark an explict module to use which seems to fail properly
	converters = ["deark[module:ripicon]"];
}
