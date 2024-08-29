import {Format} from "../../Format.js";

export class greenstreetDrawing extends Format
{
	name        = "Greenstreet Drawing";
	ext         = [".art"];
	magic       = ["Greenstreet Art drawing", /^fmt\/1877( |$)/];
	unsupported = true;
}
