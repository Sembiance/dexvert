import {Format} from "../../Format.js";

export class proShapeDrawing extends Format
{
	name        = "ProShape Drawing";
	ext         = [".psp"];
	magic       = ["ProShape drawing"];
	unsupported = true;
}
