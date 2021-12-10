import {Format} from "../../Format.js";

export class microfoxPUT extends Format
{
	name           = "Microfox PUT Archive";
	website        = "http://fileformats.archiveteam.org/wiki/PUT";
	ext            = [".put", ".ins"];
	forbidExtMatch = true;
	magic          = ["Microfox Company PUT compressed archive", "PUT archive data"];
	converters     = ["microfoxGET"];
}
