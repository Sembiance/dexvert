import {Format} from "../../Format.js";

export class qAndADocument extends Format
{
	name           = "Q&A Document";
	ext            = [".doc"];
	forbidExtMatch = true;
	magic          = ["Q and A Document", /^fmt\/1045( |$)/];
	converters     = ["strings"];
}
