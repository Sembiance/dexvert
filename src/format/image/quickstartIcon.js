import {Format} from "../../Format.js";

export class quickstartIcon extends Format
{
	name           = "Quickstart Icon";
	website        = "https://www.uninformativ.de/blog/postings/2024-08-27/0/POSTING-en.html";
	ext            = [".icn"];
	forbidExtMatch = true;
	magic          = ["Quickstart Icon"];
	converters     = ["quickstartIcon2Farbfeld"];
}
