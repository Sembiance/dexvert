import {Format} from "../../Format.js";

export class telepaint extends Format
{
	name        = "Telepaint";
	ext         = [".ss", ".st"];
	magic       = ["Telepaint canvas/stamp bitmap"];
	unsupported = true;
}