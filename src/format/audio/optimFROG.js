
import {Format} from "../../Format.js";

export class optimFROG extends Format
{
	name           = "OptimFROG";
	website        = "http://fileformats.archiveteam.org/wiki/OptimFROG";
	ext            = [".ofr", ".ofs"];
	forbidExtMatch = true;
	magic          = ["OptimFROG encoded audio"];
	converters     = ["optimFROG"];
}
