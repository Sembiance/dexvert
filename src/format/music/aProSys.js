import {Format} from "../../Format.js";

export class aProSys extends Format
{
	name        = "AProSys Module";
	ext         = [".amx", ".aps"];
	matchPreExt = true;
	magic       = ["AProSys module", /^AProSys⇥module$/];
	unsupported = true;
}
