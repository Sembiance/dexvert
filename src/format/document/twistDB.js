import {Format} from "../../Format.js";

export class twistDB extends Format
{
	name           = "Twist Database file";
	ext            = [".db"];
	forbidExtMatch = true;
	magic          = ["Twist DataBase"];
	converters     = ["strings"];
}
