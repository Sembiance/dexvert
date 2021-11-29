import {Format} from "../../Format.js";

export class jamMessageAreaHeaderFile extends Format
{
	name           = "JAM Message Area Header File";
	ext            = [".jhr"];
	forbidExtMatch = true;
	magic          = ["JAM message area header file"];
	converters     = ["strings"];
}
