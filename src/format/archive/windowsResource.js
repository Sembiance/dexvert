import {Format} from "../../Format.js";

export class windowsResource extends Format
{
	name           = "Windows Resource";
	website        = "http://fileformats.archiveteam.org/wiki/Windows_resource";
	ext            = [".res"];
	forbidExtMatch = true;
	magic          = ["MSVC .res", "Windows compiled resource", "Windows Resourcedatei"];
	notes          = "There is probably a better way to open these, maybe visual studio?";
	converters     = ["totalCommander", "resourceHacker", "strings[matchType:magic]"];	// converter after resourceHacker was resourceEditor but it's not working right now
}
