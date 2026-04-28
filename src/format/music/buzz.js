import {Format} from "../../Format.js";

export class buzz extends Format
{
	name           = "Jeskola Buzz Module";
	ext            = [".bmx", ".bmw"];
	forbidExtMatch = true;
	magic          = ["Jeskola Buzz song"];
	converters     = ["vibe2wav"];
	notes          = "Only audio samples are extracted right now, the song is not rendered.";
}
