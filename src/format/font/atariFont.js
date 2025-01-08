import {Format} from "../../Format.js";

export class atariFont extends Format
{
	name       = "Atari 8-bit/ST Font";
	ext        = [".fnt"];
	priority   = this.PRIORITY.LOW;
	fallback   = true;
	converters = ["recoil2png"];
}
