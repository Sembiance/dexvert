import {Format} from "../../Format.js";

export class lhwarp extends Format
{
	name       = "Lhwarp";
	ext        = [".lhw"];
	magic      = ["Lhwarp compressed disk image", /^LhWarp$/];
	converters = ["unar"];
}
