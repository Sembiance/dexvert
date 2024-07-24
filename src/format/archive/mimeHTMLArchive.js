import {Format} from "../../Format.js";

export class mimeHTMLArchive extends Format
{
	name           = "MIME HTML Archive";
	ext            = [".mht"];
	forbidExtMatch = true;
	magic          = ["MIME HTML archive format", /^x-fmt\/429( |$)/];
	weakMagic      = true;
	converters     = ["ripmime"];
}
