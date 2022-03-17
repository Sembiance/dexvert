import {Format} from "../../Format.js";

export class vxRexxInfo extends Format
{
	name           = "VX-REXX Windows/Object Info";
	ext            = [".vry", ".vrw"];
	forbidExtMatch = true;
	magic          = ["VX-REXX windows/object info"];
	converters     = ["strings"];
}
