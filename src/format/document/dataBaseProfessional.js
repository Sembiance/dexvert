import {Format} from "../../Format.js";

export class dataBaseProfessional extends Format
{
	name           = "DataBase Professional Database";
	ext            = [".db"];
	forbidExtMatch = true;
	magic          = ["DataBase Professional database"];
	converters     = ["strings"];
}
