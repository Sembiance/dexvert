import {Format} from "../../Format.js";

export class objectVisionDatafile extends Format
{
	name           = "ObjectVision Datafile";
	ext            = [".ovd"];
	forbidExtMatch = true;
	magic          = ["ObjectVision Datafile"];
	converters     = ["strings"];
}
