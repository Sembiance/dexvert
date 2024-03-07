import {Format} from "../../Format.js";

export class reg extends Format
{
	name           = "Windows Registry Data";
	website        = "http://fileformats.archiveteam.org/wiki/Windows_Registry";
	ext            = [".reg", ".dat"];
	forbidExtMatch = true;
	magic          = [/^Windows Registry (Data|text)/, "Windows Registry Datei"];
	untouched      = true;
	metaProvider   = ["text"];
}
