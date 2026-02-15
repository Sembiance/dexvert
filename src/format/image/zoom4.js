import {Format} from "../../Format.js";

export class zoom4 extends Format
{
	name       = "Zoom-4";
	ext        = [".zm4"];
	converters = ["recoil2png[format:ZM4]"];
}
