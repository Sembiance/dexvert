import {Format} from "../../Format.js";

export class wraptor extends Format
{
	name           = "WRAptor Archive";
	ext            = [".wra", ".wr3"];
	forbidExtMatch = true;
	magic          = ["WRAptor compressed", "WRAptor packer", /^fmt\/1611( |$)/];
	converters     = ["unWraptor"];
}
