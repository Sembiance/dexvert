import {Format} from "../../Format.js";

export class mindjonggIPG extends Format
{
	name           = "Mindjongg IPG";
	ext            = [".ipg"];
	forbidExtMatch = true;
	magic          = ["Mindjongg :ipg:"];
	converters     = ["nconvert[extractAll][format:ipg]"];
}
