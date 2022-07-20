import {Format} from "../../Format.js";

export class vendInfo extends Format
{
	name       = "VENDINFO Data Record";
	magic      = ["VENDINFO data record"];
	converters = ["strings"];
}
