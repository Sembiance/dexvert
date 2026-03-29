import {Format} from "../../Format.js";

export class netscapeSNM extends Format
{
	name           = "Netscape SNM Archive";
	ext            = [".snm"];
	forbidExtMatch = true;
	magic          = ["Netscape folder cache", "Netscape Mail Message"];
	converters     = ["unNetscapeSNM"];
}
