import {Format} from "../../Format.js";

export class malieGFBitmap extends Format
{
	name           = "MalieGF Bitmap";
	ext            = [".mgf"];
	forbidExtMatch = true;
	magic          = ["MalieGF bitmap", "image:Malie.MgfFormat"];
	converters     = ["wuimg[format:png]", "GARbro[types:image:Malie.MgfFormat]"];
}
