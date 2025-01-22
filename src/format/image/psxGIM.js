import {Format} from "../../Format.js";

export class psxGIM extends Format
{
	name       = "PlayStation Graphics Image Map";
	website    = "https://web.archive.org/web/20230817135907/http://wiki.xentax.com/index.php/GIM_Image";
	ext        = [".gim"];
	magic      = ["PlayStation Graphics Image Map"];
	converters = ["gim2png", "noesis[type:image]"];
}
