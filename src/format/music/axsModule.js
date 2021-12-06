import {Format} from "../../Format.js";

export class axsModule extends Format
{
	name        = "AXS Module";
	ext         = [".axs"];
	magic       = ["AXS module"];
	unsupported = true;
}
