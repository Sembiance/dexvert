import {Format} from "../../Format.js";

export class openGEX extends Format
{
	name       = "Open Game Engine Exchance";
	website    = "https://opengex.org/";
	ext        = [".ogex"];
	converters = ["assimp"];
}
