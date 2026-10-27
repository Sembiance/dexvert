import {Format} from "../../Format.js";

export class digitalSymphonySoundSample extends Format
{
	name       = "Digital Symphony Sound Sample";
	magic      = [/^Digital Symphony sound sample/];
	converters = ["vibe2wav[renameOut]"];
}
