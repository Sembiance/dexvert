import {Format} from "../../Format.js";

export class sinclairBASIC extends Format
{
	name       = "ZX81 Sinclair BASIC";
	ext        = [".p"];
	converters = ["recoil2png[format:P]"];

	// Due to not having no magic, we reject any created images less than 2 colors
	verify = ({meta}) => meta.colorCount>1;
}
