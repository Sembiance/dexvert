import {Format} from "../../Format.js";

export class texInfo extends Format
{
	name       = "Texinfo Document";
	ext        = [".texinfo", ".texi"];
	magic      = ["TeX document", "Texinfo source"];
	converters = ["texi2pdf", "texi2html", "strings"];
}
