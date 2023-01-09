import {Format} from "../../Format.js";

export class uflEditor extends Format
{
	name       = "UFLI-editor";
	ext        = [".ufl"];
	converters = ["recoil2png"];
}
