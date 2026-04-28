import {Format} from "../../Format.js";

export class cba extends Format
{
	name           = "Chuck Biscuits/Black Artist Module";
	ext            = [".cba"];
	forbidExtMatch = true;
	magic          = ["Chuck Biscuits/Black Artist module"];
	converters     = ["openmpt123"];
}
