import {Format} from "../../Format.js";

export class elementZX extends Format
{
	name       = "eLeMeNt ZX";
	ext        = [".hgl", ".hgh", ".skl", ".xkl", ".hrx"];
	converters = ["recoil2png"];
}
