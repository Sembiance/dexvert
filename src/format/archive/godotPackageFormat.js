import {Format} from "../../Format.js";

export class godotPackageFormat extends Format
{
	name           = "Godot Package format";
	ext            = [".pck"];
	forbidExtMatch = true;
	magic          = ["Godot Package format", "Archive: Godot Pack", /^geArchive: PCK_GDPC( |$)/];
	weakMagic      = ["Godot Package format", "Archive: Godot Pack"];
	converters     = ["gameextractor[codes:PCK_GDPC]"];
}
