import {Format} from "../../Format.js";

export class zxp extends Format
{
	name       = "ZX-Paintbrush";
	website    = "https://sourcesolutions.itch.io/zx-paintbrush";
	ext        = [".zxp"];
	magic      = ["ZX-Paintbrush"];
	converters = ["recoil2png"];
}
