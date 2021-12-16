import {Format} from "../../Format.js";

export class intelliFont extends Format
{
	name        = "IntelliFont Font";
	website     = "http://fileformats.archiveteam.org/wiki/IntelliFont";
	ext         = [".lib", ".type"];
	magic       = ["Intellifont font"];
	unsupported = true;
}
