import {Format} from "../../Format.js";

export class ibmBookManagerBook extends Format
{
	name           = "IBM BookManager Book";
	ext            = [".boo"];
	forbidExtMatch = true;
	magic          = ["IBM BookManager Book"];
	converters     = ["boo_transmog -> boo2html[skipVerify]", "boo2html[skipVerify]"];
}
