import {Format} from "../../Format.js";

export class profi extends Format
{
	name       = "ZX Spectrum Profi";
	ext        = [".grf"];
	priority   = this.PRIORITY.LOW;
	converters = ["recoil2png"];
}
