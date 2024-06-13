import {Format} from "../../Format.js";

export class rollerCoasterTycoonPicture extends Format
{
	name       = "RollerCoaster Tycoon Picture";
	ext        = [".tp4"];
	magic      = ["RollerCoaster Tycoon Track Picture/screenshot"];
	converters = ["paintDotNet"];
}
