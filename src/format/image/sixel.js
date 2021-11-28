import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class sixel extends Format
{
	name       = "Sixel";
	website    = "https://en.wikipedia.org/wiki/Sixel";
	ext        = [".six", ".sixel"];
	mimeType   = "image/x-sixel";
	magic      = TEXT_MAGIC;
	weakMagic  = true;
	converters = [`abydosconvert[format:${this.mimeType}]`];
}
