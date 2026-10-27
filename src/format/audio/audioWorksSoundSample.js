import {Format} from "../../Format.js";

export class audioWorksSoundSample extends Format
{
	name       = "AudioWorks Sound Sample";
	magic      = ["AudioWorks sound sample"];
	converters = ["vibe2wav[renameOut]"];
}
