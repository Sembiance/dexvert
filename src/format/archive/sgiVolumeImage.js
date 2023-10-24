import {Format} from "../../Format.js";

export class sgiVolumeImage extends Format
{
	name           = "SGI Volume Image";
	ext            = [".img"];
	forbidExtMatch = true;
	magic          = ["SGI volume image", "SGI disk label"];
	priority       = this.PRIORITY.TOP;
	converters     = ["uniso[block:512][checkMount]"];
}
