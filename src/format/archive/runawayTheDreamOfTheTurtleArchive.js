import {Format} from "../../Format.js";

export class runawayTheDreamOfTheTurtleArchive extends Format
{
	name           = "Runaway: The Dream of the Turtle Archive";
	ext            = [".000"];
	forbidExtMatch = true;
	magic          = [/^geArchive: 000_6( |$)/];
	converters     = ["gameextractor[codes:000_6]"];
}
