import {Format} from "../../Format.js";

export class a2gsPreferred extends Format
{
	name       = "Apple IIGS Preferred Format";
	ext        = [".gs", ".iigs", ".pnt", ".shr"];
	magic      = ["Apple IIGS Preferred Format"];
	converters = ["recoil2png"];
}
