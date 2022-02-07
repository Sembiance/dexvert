import {Format} from "../../Format.js";

export class windowsResource extends Format
{
	name       = "Windows Resource";
	website    = "http://fileformats.archiveteam.org/wiki/Windows_resource";
	ext        = [".res"];
	weakExt    = true;
	magic      = ["MSVC .res", "Windows compiled resource"];
	notes      = "There is probably a better way to open these, maybe visual studio?";
	converters = dexState => ["resourceHacker", "resourceEditor", ...(dexState.phase.id.matchType==="magic" ? ["strings"] : [])];
}
