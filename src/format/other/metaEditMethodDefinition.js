import {Format} from "../../Format.js";

export class metaEditMethodDefinition extends Format
{
	name           = "MetaEdit Method Definition";
	ext            = [".mof"];
	forbidExtMatch = true;
	magic          = ["MetaEdit Method definition"];
	converters     = ["strings"];
}
