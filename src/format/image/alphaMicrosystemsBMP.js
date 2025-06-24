import {Format} from "../../Format.js";

export class alphaMicrosystemsBMP extends Format
{
	name           = "Alpha Microsystems BMP";
	ext            = [".bmp"];
	forbidExtMatch = true;
	magic          = ["Alpha Microsystems Bitmap", "deark: alphabmp (Alpha Microsystems BMP)", "Alpha Microsystems BMP :abmp:"];
	converters     = ["deark[module:alphabmp]", "nconvert[format:abmp]"];
}
