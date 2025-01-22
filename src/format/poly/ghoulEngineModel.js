import {Format} from "../../Format.js";

export class ghoulEngineModel extends Format
{
	name           = "GHOUL Engine model";
	ext            = [".ghb"];
	forbidExtMatch = true;
	magic          = ["GHOUL Engine model"];
	converters     = ["noesis[type:poly]"];
}
