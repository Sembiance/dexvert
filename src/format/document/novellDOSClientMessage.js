import {Format} from "../../Format.js";

export class novellDOSClientMessage extends Format
{
	name           = "Novell DOS Client Message";
	ext            = [".msg"];
	forbidExtMatch = true;
	magic          = ["Novell DOS client message"];
	converters     = ["strings"];
}
