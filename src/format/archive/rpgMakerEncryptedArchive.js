import {Format} from "../../Format.js";

export class rpgMakerEncryptedArchive extends Format
{
	name       = "RPG Maker Encrypted Archive";
	ext        = [".rgss2a", ".rgss3a", ".rgssad"];
	magic      = ["RPG Maker VX encrypted Archive"];
	converters = ["rgssExtractor"];
}
