import {Format} from "../../Format.js";

export class klystrack extends Format
{
	name        = "Klystrack Module";
	ext         = [".kt"];
	magic       = ["Klystrack chiptune", "Klystrack song"];
	unsupported = true;
}
