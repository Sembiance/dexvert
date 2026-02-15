import {Format} from "../../Format.js";

export class samCoupeSSX extends Format
{
	name       = "Sam Coupe SSX";
	ext        = [".ssx"];
	converters = ["recoil2png[format:SSX]"];
}
