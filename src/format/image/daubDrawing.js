import {Format} from "../../Format.js";

export class daubDrawing extends Format
{
	name        = "DAUB Drawing";
	ext         = [".dob"];
	magic       = ["DAUB drawing"];
	unsupported = true;
}
