import {Format} from "../../Format.js";

export class softHouseSprite extends Format
{
	name           = "Soft House Sprite Bitmap";
	ext            = [".pic"];
	forbidExtMatch = true;
	magic          = ["image:Sprite.PicFormat"];
	converters     = ["GARbro[types:image:Sprite.PicFormat]"];
}
