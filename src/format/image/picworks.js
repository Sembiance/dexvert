import {Format} from "../../Format.js";

export class picworks extends Format
{
	name       = "Picworks";
	ext        = [".cp3"];
	converters = ["recoil2png[format:CP3]"];
	verify     = ({meta}) => meta.width===640 && meta.height===400;	// with a weak extension only match, ensure it's the expected 640x400 size
}
