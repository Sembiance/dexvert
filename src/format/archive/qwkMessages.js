import {Format} from "../../Format.js";

export class qwkMessages extends Format
{
	name       = "QWK Messages";
	filename   = [/^messages\.dat$/i];
	magic      = ["QWK Messages"];
	converters = ["vibeExtract"];
}
