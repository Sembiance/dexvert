import {Format} from "../../Format.js";

export class psxGIM extends Format
{
	name           = "PlayStation Graphics Image Map";
	website        = "https://web.archive.org/web/20230817135907/http://wiki.xentax.com/index.php/GIM_Image";
	ext            = [".gim"];
	forbidExtMatch = true;
	magic          = ["PlayStation Graphics Image Map", "image:Psp.GimFormat"];
	converters     = ["gim2png", "GARbro[types:image:Psp.GimFormat]", "noesis[type:image]"];
}
