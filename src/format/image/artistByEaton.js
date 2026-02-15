import {Format} from "../../Format.js";

export class artistByEaton extends Format
{
	name       = "Artist by David Eaton";
	ext        = [".art"];
	priority   = this.PRIORITY.LOW;
	converters = ["recoil2png[format:ART.Atari8Artist]"];
}
