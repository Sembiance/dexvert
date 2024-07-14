import {Format} from "../../Format.js";

export class mimeEntity extends Format
{
	name       = "MIME Entity";
	magic      = [/^MIME entity/];
	converters = ["unmime"];
}
