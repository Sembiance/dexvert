import {Format} from "../../Format.js";

export class envoy extends Format
{
	name       = "Envoy Document";
	website    = "https://en.wikipedia.org/wiki/Envoy_(WordPerfect)";
	ext        = [".evy"];
	magic      = ["Envoy document"];
	converters = ["envoyViewer"];
}
