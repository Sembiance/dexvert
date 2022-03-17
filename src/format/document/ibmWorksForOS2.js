import {Format} from "../../Format.js";

export class ibmWorksForOS2 extends Format
{
	name           = "IBM Works for OS/2";
	ext            = [".lwp", ".lpw"];
	forbidExtMatch = true;
	magic          = ["IBM Works for OS/2 word processor document"];
	converters     = ["strings"];
}
