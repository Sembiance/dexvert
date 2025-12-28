import {xu} from "xu";
import {Format} from "../../Format.js";

export class amosPicturePacker extends Format
{
	name           = "AMOS Picture Packer";
	ext            = [".bin"];
	forbidExtMatch = true;
	mimeType       = "image/x-amos-picturepacker";
	priority       = this.PRIORITY.LOW;
	magic          = ["deark: abk (AMOS picture"];
	converters     = [`abydosconvert[format:${this.mimeType}]`, "deark[module:abk][opt:abk:allownopal]"];	// abydos guesses on palette for some, which is usually right, so just stick with it for now
}
